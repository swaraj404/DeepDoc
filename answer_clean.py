import os
import logging
from typing import List, Dict, Optional
from sentence_transformers import SentenceTransformer
import chromadb
from dotenv import load_dotenv
from functools import lru_cache
import time

# Local AI import
try:
    from transformers import pipeline
    HAS_TRANSFORMERS = True
except ImportError:
    HAS_TRANSFORMERS = False

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AnswerRetriever:
    """
    Streamlined Document Q&A system using ChromaDB and Local AI
    """
    
    def __init__(self, database_path: str = "./database"):
        """Initialize with database path"""
        self.database_path = database_path
        self.collection_name = "pdf_embeddings"
        self.similarity_threshold = float(os.getenv('SIMILARITY_THRESHOLD', 0.01))
        self.max_retries = int(os.getenv('MAX_RETRIES', 3))
        self.retry_delay = int(os.getenv('RETRY_DELAY', 1))
        
        # Initialize components
        self.model = None
        self.collection = None
        self.local_pipeline = None
        
        # Setup
        self._setup_embedding_model()
        self._setup_database()
        self._setup_local_ai()
    
    def _setup_embedding_model(self):
        """Initialize sentence transformer model"""
        try:
            model_name = os.getenv('SENTENCE_MODEL', 'sentence-transformers/all-MiniLM-L6-v2')
            self.model = SentenceTransformer(model_name)
            logger.info(f"Loaded sentence transformer model: {model_name}")
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            raise
    
    def _setup_database(self):
        """Initialize ChromaDB connection"""
        try:
            client = chromadb.PersistentClient(path=self.database_path)
            self.collection = client.get_collection(self.collection_name)
            logger.info(f"Connected to ChromaDB at {self.database_path}")
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise
    
    def _setup_local_ai(self):
        """Initialize local AI model"""
        try:
            if HAS_TRANSFORMERS:
                model_name = os.getenv('LOCAL_MODEL', 'google/flan-t5-base')
                self.local_pipeline = pipeline(
                    "text2text-generation",
                    model=model_name,
                    device_map="auto"
                )
                logger.info(f"Initialized local model: {model_name}")
        except Exception as e:
            logger.warning(f"Local AI setup failed: {e}")
    
    def get_current_provider(self) -> str:
        """Get current AI provider"""
        return "local"
    
    @lru_cache(maxsize=100)
    def get_query_embedding(self, query: str) -> List[float]:
        """Generate and cache query embeddings"""
        try:
            embedding = self.model.encode([query])[0].tolist()
            return embedding
        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
            return []
    
    def retrieve_relevant_chunks(self, query: str, marks: int = 3, max_chunks: int = None) -> List[Dict]:
        """Retrieve relevant document chunks"""
        try:
            # Determine number of chunks based on marks
            if max_chunks is None:
                max_chunks = min(marks * 2, 10)
            
            # Get query embedding
            query_embedding = self.get_query_embedding(query)
            if not query_embedding:
                return []
            
            # Query ChromaDB
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=max_chunks,
                include=['documents', 'metadatas', 'distances']
            )
            
            chunks = []
            if results['documents'] and results['documents'][0]:
                for i, (doc, metadata, distance) in enumerate(zip(
                    results['documents'][0],
                    results['metadatas'][0],
                    results['distances'][0]
                )):
                    # Convert distance to similarity
                    similarity = 1 - distance
                    
                    # Filter by similarity threshold
                    if similarity >= self.similarity_threshold:
                        chunks.append({
                            'content': doc,
                            'metadata': metadata or {},
                            'similarity': similarity,
                            'rank': i + 1
                        })
            
            logger.info(f"Retrieved {len(chunks)} relevant chunks")
            return chunks
            
        except Exception as e:
            logger.error(f"Error retrieving chunks: {e}")
            return []
    
    def generate_answer(self, query: str, chunks: List[Dict]) -> Optional[str]:
        """Generate answer using local AI"""
        if not chunks:
            return "I don't have enough relevant information to answer this question."
        
        # Simple context preparation for local model
        context_parts = []
        for chunk in chunks[:3]:  # Limit to 3 chunks
            context_parts.append(chunk['content'])
        
        context = " ".join(context_parts)
        prompt = f"Context: {context}\n\nQuestion: {query}\n\nAnswer:"
        
        try:
            if self.local_pipeline:
                response = self.local_pipeline(
                    prompt,
                    max_length=200,
                    temperature=0.3,
                    do_sample=False,
                    truncation=True,
                    pad_token_id=self.local_pipeline.tokenizer.eos_token_id
                )
                
                if response and len(response) > 0:
                    generated_text = response[0]['generated_text'].strip()
                    
                    # Clean response
                    if generated_text.startswith(prompt):
                        generated_text = generated_text[len(prompt):].strip()
                    
                    # Simple deduplication
                    sentences = generated_text.split('.')
                    seen = set()
                    cleaned = []
                    
                    for sentence in sentences:
                        sentence = sentence.strip()
                        if sentence and sentence not in seen and len(sentence) > 5:
                            seen.add(sentence)
                            cleaned.append(sentence)
                    
                    if cleaned:
                        result = '. '.join(cleaned)
                        if not result.endswith('.'):
                            result += '.'
                        return result
                    
                    return generated_text if generated_text else "Unable to generate answer."
            
            # Fallback if no local AI
            return f"Based on the available context: {context[:200]}..."
            
        except Exception as e:
            logger.error(f"Answer generation failed: {e}")
            return "Sorry, I encountered an error while generating the answer."
    
    def calculate_confidence(self, chunks: List[Dict], marks: int = 3) -> float:
        """Calculate confidence score"""
        if not chunks:
            return 0.0
        
        # Base confidence from similarity scores
        avg_similarity = sum(chunk['similarity'] for chunk in chunks) / len(chunks)
        
        # Boost for local AI (4x multiplier)
        confidence = avg_similarity * 4.0
        
        # Boost for more chunks
        chunk_boost = min(len(chunks) * 0.1, 0.3)
        confidence += chunk_boost
        
        # Cap at 1.0
        return min(confidence, 1.0)
    
    def get_answer_with_sources(self, query: str, marks: int = 3, include_sources: bool = False) -> Dict:
        """
        Main method to get answer with sources
        
        Args:
            query: User question
            marks: Question complexity (2-5)
            include_sources: Whether to include source information
            
        Returns:
            Dictionary with answer, confidence, success status
        """
        try:
            # Retrieve relevant chunks
            chunks = self.retrieve_relevant_chunks(query, marks)
            
            if not chunks:
                return {
                    'success': False,
                    'answer': "I don't have enough relevant information to answer this question. Please try rephrasing or provide more context.",
                    'confidence': 0.0,
                    'chunks_used': 0,
                    'error': 'No relevant chunks found'
                }
            
            # Generate answer
            answer = self.generate_answer(query, chunks)
            
            if not answer:
                return {
                    'success': False,
                    'answer': "I couldn't generate a proper answer. Please try again.",
                    'confidence': 0.0,
                    'chunks_used': len(chunks),
                    'error': 'Answer generation failed'
                }
            
            # Calculate confidence
            confidence = self.calculate_confidence(chunks, marks)
            
            result = {
                'success': True,
                'answer': answer,
                'confidence': confidence,
                'chunks_used': len(chunks)
            }
            
            # Add sources if requested
            if include_sources:
                sources = []
                for chunk in chunks:
                    source_info = {
                        'content': chunk['content'][:200] + "..." if len(chunk['content']) > 200 else chunk['content'],
                        'source': chunk['metadata'].get('source', 'Unknown'),
                        'similarity': chunk['similarity']
                    }
                    sources.append(source_info)
                result['sources'] = sources
            
            return result
            
        except Exception as e:
            logger.error(f"Error generating answer: {e}")
            return {
                'success': False,
                'answer': f"An error occurred while processing your question: {str(e)}",
                'confidence': 0.0,
                'chunks_used': 0,
                'error': str(e)
            }
