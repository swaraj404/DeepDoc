#!/usr/bin/env python3
"""
Command-line database inspector for DeepDoc
Usage: python db_inspector.py [command]
"""

import sys
import chromadb
import json
from pathlib import Path
from datetime import datetime

def print_header(title):
    print("\n" + "="*50)
    print(f"  {title}")
    print("="*50)

def show_database_info():
    """Show general database information"""
    print_header("DATABASE OVERVIEW")
    
    db_path = "./database"
    
    try:
        # Check if database exists
        if not Path(db_path).exists():
            print("❌ Database folder not found at ./database")
            return
        
        print(f"📍 Database Location: {Path(db_path).absolute()}")
        
        # Connect to database
        client = chromadb.PersistentClient(path=db_path)
        collections = client.list_collections()
        
        print(f"📚 Collections Found: {len(collections)}")
        
        for collection in collections:
            print(f"\n  Collection: {collection.name}")
            print(f"  ID: {collection.id}")
            print(f"  Documents: {collection.count()}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def show_collection_details(collection_name="pdf_embeddings"):
    """Show detailed collection information"""
    print_header(f"COLLECTION: {collection_name}")
    
    try:
        client = chromadb.PersistentClient(path="./database")
        collection = client.get_collection(collection_name)
        
        print(f"📊 Total Documents: {collection.count()}")
        
        # Get sample data
        results = collection.get(limit=5, include=['documents', 'metadatas'])
        
        if results['documents']:
            print(f"🔍 Embedding Dimension: {len(collection.get(limit=1, include=['embeddings'])['embeddings'][0])}")
            
            print("\n📄 Sample Documents:")
            for i, (doc, metadata) in enumerate(zip(results['documents'], results['metadatas'])):
                print(f"\n  Document {i+1}:")
                print(f"  Content: {doc[:100]}...")
                if metadata:
                    print(f"  Source: {metadata.get('source', 'Unknown')}")
                    print(f"  Metadata: {json.dumps(metadata, indent=2)}")
        else:
            print("⚠️ No documents found in collection")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def show_sources():
    """Show all unique sources in the database"""
    print_header("DOCUMENT SOURCES")
    
    try:
        client = chromadb.PersistentClient(path="./database")
        collection = client.get_collection("pdf_embeddings")
        
        # Get all metadata
        all_data = collection.get(include=['metadatas'])
        
        sources = {}
        for metadata in all_data['metadatas']:
            if metadata and 'source' in metadata:
                source = metadata['source']
                sources[source] = sources.get(source, 0) + 1
        
        if sources:
            print(f"📚 Found {len(sources)} unique sources:")
            for source, count in sorted(sources.items()):
                print(f"  📄 {source}: {count} chunks")
        else:
            print("⚠️ No source information found")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def search_database(query, limit=5):
    """Search the database for similar content"""
    print_header(f"SEARCH RESULTS: '{query}'")
    
    try:
        # Import the answer retriever
        from answer import AnswerRetriever
        
        retriever = AnswerRetriever()
        chunks = retriever.retrieve_relevant_chunks(query, max_chunks=limit)
        
        if chunks:
            print(f"🔍 Found {len(chunks)} relevant chunks:")
            for i, chunk in enumerate(chunks):
                print(f"\n  Result {i+1}:")
                print(f"  Similarity: {chunk.get('similarity', 0):.3f}")
                print(f"  Source: {chunk['metadata'].get('source', 'Unknown')}")
                print(f"  Content: {chunk['content'][:200]}...")
        else:
            print("⚠️ No relevant chunks found")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def show_help():
    """Show help information"""
    print_header("DATABASE INSPECTOR HELP")
    print("""
Available commands:
  info        - Show database overview
  details     - Show collection details
  sources     - List all document sources
  search <query> - Search for content
  help        - Show this help message

Examples:
  python db_inspector.py info
  python db_inspector.py search "artificial intelligence"
  python db_inspector.py sources
    """)

def main():
    if len(sys.argv) < 2:
        show_database_info()
        return
    
    command = sys.argv[1].lower()
    
    if command == "info":
        show_database_info()
    elif command == "details":
        show_collection_details()
    elif command == "sources":
        show_sources()
    elif command == "search":
        if len(sys.argv) < 3:
            print("❌ Please provide a search query")
            return
        query = " ".join(sys.argv[2:])
        search_database(query)
    elif command == "help":
        show_help()
    else:
        print(f"❌ Unknown command: {command}")
        show_help()

if __name__ == "__main__":
    main()
