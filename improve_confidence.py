#!/usr/bin/env python3
"""
Re-embed documents to improve confidence scores
This script will re-process all documents with the current embedding model
"""

import os
import logging
from dotenv import load_dotenv
from ingest import ImprovedIngestDoc
from answer import ImprovedAnswerRetriever
import chromadb

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def backup_current_database():
    """Create a backup of current database"""
    import shutil
    import datetime
    
    backup_name = f"database_backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
    try:
        if os.path.exists('./database'):
            shutil.copytree('./database', f'./{backup_name}')
            logger.info(f"Database backed up to {backup_name}")
            return backup_name
    except Exception as e:
        logger.error(f"Backup failed: {e}")
    return None

def clear_current_collection():
    """Clear the current collection"""
    try:
        client = chromadb.PersistentClient(path='./database')
        collection = client.get_collection('pdf_embeddings')
        
        # Get all IDs
        all_data = collection.get()
        if all_data['ids']:
            collection.delete(ids=all_data['ids'])
            logger.info(f"Cleared {len(all_data['ids'])} existing chunks")
        else:
            logger.info("Collection was already empty")
            
    except Exception as e:
        logger.error(f"Error clearing collection: {e}")

def get_original_pdfs_info():
    """Get information about documents to re-process"""
    try:
        client = chromadb.PersistentClient(path='./database')
        collection = client.get_collection('pdf_embeddings')
        
        # Get sample of documents to see what we have
        results = collection.get(limit=100, include=['metadatas'])
        
        sources = set()
        file_paths = set()
        
        for metadata in results.get('metadatas', []):
            if metadata:
                if 'source' in metadata:
                    sources.add(metadata['source'])
                if 'file_path' in metadata:
                    file_paths.add(metadata['file_path'])
        
        logger.info(f"Found {len(sources)} unique documents")
        for source in list(sources)[:10]:  # Show first 10
            logger.info(f"  - {source}")
            
        return sources, file_paths
        
    except Exception as e:
        logger.error(f"Error getting document info: {e}")
        return set(), set()

def re_embed_documents():
    """Re-embed all documents with current model"""
    print("🔄 Re-embedding Documents for Better Confidence")
    print("=" * 50)
    
    # Step 1: Backup current database
    print("\n1. Creating backup...")
    backup_name = backup_current_database()
    
    # Step 2: Get info about current documents
    print("\n2. Analyzing current documents...")
    sources, file_paths = get_original_pdfs_info()
    
    if not sources:
        print("❌ No documents found to re-embed")
        return
    
    # Step 3: Clear current collection
    print(f"\n3. Clearing current collection ({len(sources)} documents)...")
    clear_current_collection()
    
    # Step 4: Check for available PDF files
    print("\n4. Looking for PDF files to re-process...")
    
    # Look in common locations
    pdf_locations = [
        './pdfs',
        './documents', 
        './data',
        './',
        '~/Downloads'
    ]
    
    found_pdfs = []
    for location in pdf_locations:
        if os.path.exists(location):
            for file in os.listdir(location):
                if file.lower().endswith('.pdf'):
                    found_pdfs.append(os.path.join(location, file))
    
    if found_pdfs:
        print(f"✅ Found {len(found_pdfs)} PDF files to re-process")
        
        # Step 5: Re-ingest with current model
        print("\n5. Re-ingesting documents with current embedding model...")
        ingestor = ImprovedIngestDoc()
        
        success_count = 0
        for pdf_path in found_pdfs:
            try:
                filename = os.path.basename(pdf_path)
                document_id = os.path.splitext(filename)[0]
                
                print(f"  Processing: {filename}")
                success = ingestor.save_document_to_db(pdf_path, document_id)
                
                if success:
                    success_count += 1
                    print(f"    ✅ Success")
                else:
                    print(f"    ❌ Failed")
                    
            except Exception as e:
                print(f"    ❌ Error: {e}")
        
        print(f"\n✅ Re-embedded {success_count}/{len(found_pdfs)} documents")
        
        # Step 6: Test new confidence scores
        print("\n6. Testing new confidence scores...")
        test_confidence()
        
    else:
        print("❌ No PDF files found to re-process")
        print("\nTo improve confidence scores:")
        print("1. Place your original PDF files in a 'pdfs' folder")
        print("2. Run this script again")
        print("3. Or manually upload documents through the web interface")

def test_confidence():
    """Test confidence scores with re-embedded documents"""
    try:
        retriever = ImprovedAnswerRetriever()
        
        test_queries = [
            "What is human computer interaction?",
            "What are the main concepts?",
            "Explain the key principles"
        ]
        
        print("\nTesting confidence scores:")
        for query in test_queries:
            chunks = retriever.retrieve_relevant_chunks(query, max_chunks=3)
            if chunks:
                avg_similarity = sum(chunk.get('similarity', 0) for chunk in chunks) / len(chunks)
                print(f"  '{query[:30]}...': {avg_similarity:.3f} confidence, {len(chunks)} chunks")
            else:
                print(f"  '{query[:30]}...': No chunks found")
                
    except Exception as e:
        logger.error(f"Error testing confidence: {e}")

if __name__ == "__main__":
    re_embed_documents()
