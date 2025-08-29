
import os
import logging
import tempfile
import re
from datetime import datetime
from typing import List, Optional
from pypdf import PdfReader
import nltk
from sentence_transformers import SentenceTransformer
import chromadb
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Download required NLTK data
try:
    nltk.download("punkt", quiet=True)
except Exception as e:
    logger.warning(f"Could not download NLTK data: {e}")

class ImprovedIngestDoc:
    def __init__(self, database_path: str = None, collection_name: str = None):
        """
        Initialize the document ingestion system
        
        Args:
            database_path: Path to ChromaDB storage (defaults to env var or ./database)
            collection_name: Name of the collection (defaults to env var or pdf_embeddings)
        """
        self.database_path = database_path or os.getenv('DATABASE_PATH', './database')
        self.collection_name = collection_name or os.getenv('COLLECTION_NAME', 'pdf_embeddings')
        
        # Initialize sentence transformer model
        try:
            model_name = os.getenv('SENTENCE_MODEL', 'sentence-transformers/all-MiniLM-L6-v2')
            self.model = SentenceTransformer(model_name)
            logger.info(f"Sentence transformer model loaded successfully: {model_name}")
        except Exception as e:
            logger.error(f"Failed to load sentence transformer model: {e}")
            raise
        
        # Initialize ChromaDB
        try:
            # Ensure database directory exists
            os.makedirs(self.database_path, exist_ok=True)
            self.chroma_client = chromadb.PersistentClient(path=self.database_path)
            self.collection = self.chroma_client.get_or_create_collection(name=self.collection_name)
            logger.info(f"Connected to ChromaDB at {self.database_path}")
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {e}")
            raise
    
    def pdf_loader(self, pdf_path: str) -> Optional[str]:
        """
        Extract text from PDF file with error handling
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Extracted text or None if failed
        """
        try:
            if not os.path.exists(pdf_path):
                logger.error(f"PDF file not found: {pdf_path}")
                return None
                
            reader = PdfReader(pdf_path)
            text = ""
            
            for page_num, page in enumerate(reader.pages):
                try:
                    page_text = page.extract_text()
                    if page_text.strip():
                        text += page_text + f"\n[PAGE {page_num+1}]\n"
                except Exception as e:
                    logger.warning(f"Failed to extract text from page {page_num+1}: {e}")
                    continue
            
            if not text.strip():
                logger.error(f"No text extracted from PDF: {pdf_path}")
                return None
                
            logger.info(f"Successfully extracted text from {len(reader.pages)} pages")
            return text
            
        except Exception as e:
            logger.error(f"Failed to load PDF {pdf_path}: {e}")
            return None
    
    def smart_chunking(self, text: str, max_chunk_size: int = 500, overlap: int = 50) -> List[str]:
        """
        Improved text chunking with sentence awareness and overlap
        
        Args:
            text: Input text to chunk
            max_chunk_size: Maximum characters per chunk
            overlap: Number of characters to overlap between chunks
            
        Returns:
            List of text chunks
        """
        if not text or not text.strip():
            return []
        
        try:
            # Clean and prepare text
            lines = text.split("\n")
            cleaned_lines = []
            
            for line in lines:
                stripped = line.strip()
                if not stripped:
                    continue
                # Skip very short lines, page markers, and questions
                if (len(stripped) < 30 and not stripped.endswith('.')) or stripped.startswith('[PAGE'):
                    continue
                if stripped.endswith("?") and len(stripped) < 100:
                    continue
                cleaned_lines.append(stripped)
            
            # Join lines and create chunks
            clean_text = " ".join(cleaned_lines)
            
            # Split into sentences using NLTK if available
            try:
                sentences = nltk.sent_tokenize(clean_text)
            except:
                # Fallback to simple sentence splitting
                sentences = re.split(r'[.!?]+', clean_text)
                sentences = [s.strip() for s in sentences if s.strip()]
            
            # Create chunks with overlap
            chunks = []
            current_chunk = ""
            
            for sentence in sentences:
                # Check if adding this sentence would exceed the limit
                if len(current_chunk) + len(sentence) + 1 > max_chunk_size and current_chunk:
                    chunks.append(current_chunk.strip())
                    
                    # Create overlap by keeping last few words
                    if overlap > 0:
                        words = current_chunk.split()
                        overlap_words = words[-min(len(words), overlap//10):]  # Approximate word overlap
                        current_chunk = " ".join(overlap_words) + " " + sentence
                    else:
                        current_chunk = sentence
                else:
                    current_chunk += " " + sentence if current_chunk else sentence
            
            # Add the last chunk
            if current_chunk.strip():
                chunks.append(current_chunk.strip())
            
            # Filter out very short chunks
            chunks = [chunk for chunk in chunks if len(chunk) > 50]
            
            logger.info(f"Created {len(chunks)} text chunks")
            return chunks
            
        except Exception as e:
            logger.error(f"Error in text chunking: {e}")
            # Fallback to simple chunking
            words = text.split()
            chunks = []
            for i in range(0, len(words), max_chunk_size//10):
                chunk = " ".join(words[i:i + max_chunk_size//10])
                if len(chunk) > 50:
                    chunks.append(chunk)
            return chunks
    
    def embed_documents(self, chunks: List[str]) -> Optional[List[List[float]]]:
        """
        Generate embeddings for text chunks
        
        Args:
            chunks: List of text chunks
            
        Returns:
            List of embeddings or None if failed
        """
        if not chunks:
            logger.warning("No chunks provided for embedding")
            return None
        
        try:
            embeddings = self.model.encode(chunks)
            logger.info(f"Generated embeddings for {len(chunks)} chunks")
            return embeddings.tolist()
        except Exception as e:
            logger.error(f"Failed to generate embeddings: {e}")
            return None
    
    def save_document_to_db(self, pdf_path: str, document_id: str = None) -> bool:
        """
        Process PDF and save to vector database with metadata
        
        Args:
            pdf_path: Path to PDF file
            document_id: Unique identifier for the document
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Extract text from PDF
            text = self.pdf_loader(pdf_path)
            if not text:
                return False
            
            # Create chunks
            max_chunk_size = int(os.getenv('MAX_CHUNK_SIZE', '500'))
            chunk_overlap = int(os.getenv('CHUNK_OVERLAP', '50'))
            chunks = self.smart_chunking(text, max_chunk_size, chunk_overlap)
            
            if not chunks:
                logger.error("No valid chunks created from PDF")
                return False
            
            # Generate embeddings
            embeddings = self.embed_documents(chunks)
            if not embeddings:
                return False
            
            # Prepare document metadata
            if not document_id:
                document_id = os.path.splitext(os.path.basename(pdf_path))[0]
            
            timestamp = datetime.now().isoformat()
            base_metadata = {
                'source': document_id,
                'file_path': pdf_path,
                'timestamp': timestamp,
                'total_chunks': len(chunks)
            }
            
            # Save to ChromaDB
            ids = []
            metadatas = []
            
            for i, chunk in enumerate(chunks):
                chunk_id = f"{document_id}_chunk_{i}"
                chunk_metadata = base_metadata.copy()
                chunk_metadata.update({
                    'chunk_index': i,
                    'chunk_id': chunk_id
                })
                
                ids.append(chunk_id)
                metadatas.append(chunk_metadata)
            
            # Add to collection
            self.collection.add(
                ids=ids,
                documents=chunks,
                embeddings=embeddings,
                metadatas=metadatas
            )
            
            logger.info(f"Successfully saved {len(chunks)} chunks from {document_id} to database")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save document to database: {e}")
            return False
    
    def batch_process_documents(self, pdf_directory: str) -> dict:
        """
        Process multiple PDFs in a directory
        
        Args:
            pdf_directory: Directory containing PDF files
            
        Returns:
            Dictionary with processing results
        """
        results = {"successful": [], "failed": []}
        
        try:
            if not os.path.exists(pdf_directory):
                logger.error(f"Directory not found: {pdf_directory}")
                return results
            
            pdf_files = [f for f in os.listdir(pdf_directory) if f.lower().endswith('.pdf')]
            
            if not pdf_files:
                logger.warning(f"No PDF files found in {pdf_directory}")
                return results
            
            logger.info(f"Processing {len(pdf_files)} PDF files...")
            
            for pdf_file in pdf_files:
                pdf_path = os.path.join(pdf_directory, pdf_file)
                document_id = os.path.splitext(pdf_file)[0]
                
                logger.info(f"Processing: {pdf_file}")
                
                if self.save_document_to_db(pdf_path, document_id):
                    results["successful"].append(pdf_file)
                    logger.info(f"✅ Successfully processed: {pdf_file}")
                else:
                    results["failed"].append(pdf_file)
                    logger.error(f"❌ Failed to process: {pdf_file}")
            
            logger.info(f"Batch processing complete: {len(results['successful'])} successful, {len(results['failed'])} failed")
            return results
            
        except Exception as e:
            logger.error(f"Error in batch processing: {e}")
            return results
    
    def get_collection_stats(self) -> dict:
        """
        Get statistics about the document collection
        
        Returns:
            Dictionary with collection statistics
        """
        try:
            count = self.collection.count()
            
            # Get a sample of documents to analyze
            if count > 0:
                sample_results = self.collection.get(limit=min(count, 100))
                unique_sources = set()
                
                if sample_results.get('metadatas'):
                    for metadata in sample_results['metadatas']:
                        if metadata and 'source' in metadata:
                            unique_sources.add(metadata['source'])
            else:
                unique_sources = set()
            
            return {
                'total_chunks': count,
                'unique_documents': len(unique_sources),
                'collection_name': self.collection_name,
                'database_path': self.database_path
            }
        except Exception as e:
            logger.error(f"Error getting collection stats: {e}")
            return {'error': str(e)}

# Backward compatibility with original class name
class Ingestdoc(ImprovedIngestDoc):
    """Backward compatibility wrapper"""
    def __init__(self):
        # Use old database path for compatibility
        database_path = os.getenv('DATABASE_PATH', './SE')
        super().__init__(database_path=database_path)
    
    def tokenize_pdf(self, pdf_path: str) -> List[str]:
        """Legacy method for backward compatibility"""
        text = self.pdf_loader(pdf_path)
        if text:
            return self.smart_chunking(text)
        return []
    
    def embedd_doc(self, chunks: List[str]):
        """Legacy method for backward compatibility"""
        embeddings = self.embed_documents(chunks)
        if embeddings:
            # Return in tensor format for compatibility
            import torch
            return torch.tensor(embeddings)
        return None
    
    def save_embeddings_to_db(self, pdf_path: str) -> bool:
        """Legacy method for backward compatibility"""
        return self.save_document_to_db(pdf_path)

if __name__ == "__main__":
    # Example usage
    ingestor = ImprovedIngestDoc()
    
    # For single file (backward compatible)
    pdf_path = input("Enter PDF path (or press Enter for batch processing): ").strip()
    
    if pdf_path:
        if os.path.exists(pdf_path):
            document_id = input("Enter document ID (optional): ").strip() or None
            success = ingestor.save_document_to_db(pdf_path, document_id)
            print(f"✅ Document processed successfully!" if success else "❌ Failed to process document")
        else:
            print(f"❌ File not found: {pdf_path}")
    else:
        # Batch processing
        directory = input("Enter directory path containing PDFs: ").strip()
        if directory:
            results = ingestor.batch_process_documents(directory)
            print(f"\n📊 Batch Processing Results:")
            print(f"✅ Successful: {len(results['successful'])}")
            print(f"❌ Failed: {len(results['failed'])}")
            if results['failed']:
                print(f"Failed files: {', '.join(results['failed'])}")
    
    # Show collection stats
    stats = ingestor.get_collection_stats()
    print(f"\n📊 Collection Stats: {stats}") 