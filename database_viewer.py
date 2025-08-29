#!/usr/bin/env python3
"""
Database Viewer for DeepDoc
This script provides detailed information about the ChromaDB database
"""

import streamlit as st
import chromadb
import pandas as pd
from pathlib import Path
import json
from datetime import datetime

st.set_page_config(
    page_title="DeepDoc Database Viewer",
    page_icon="🗄️",
    layout="wide"
)

st.title("🗄️ DeepDoc Database Viewer")
st.markdown("Comprehensive view of your document database")

# Database path
db_path = "./database"

def get_database_info():
    """Get comprehensive database information"""
    try:
        client = chromadb.PersistentClient(path=db_path)
        collections = client.list_collections()
        
        info = {
            "database_path": str(Path(db_path).absolute()),
            "database_exists": Path(db_path).exists(),
            "collections": []
        }
        
        for collection in collections:
            coll_info = {
                "name": collection.name,
                "count": collection.count(),
                "id": collection.id
            }
            info["collections"].append(coll_info)
        
        return info
    except Exception as e:
        return {"error": str(e)}

def get_collection_details(collection_name="pdf_embeddings"):
    """Get detailed information about a collection"""
    try:
        client = chromadb.PersistentClient(path=db_path)
        collection = client.get_collection(collection_name)
        
        # Get sample documents
        results = collection.get(
            limit=10,
            include=['documents', 'metadatas', 'embeddings']
        )
        
        return {
            "name": collection_name,
            "count": collection.count(),
            "sample_docs": results['documents'],
            "sample_metadata": results['metadatas'],
            "embedding_dimension": len(results['embeddings'][0]) if results['embeddings'] else 0,
            "sample_ids": results['ids']
        }
    except Exception as e:
        return {"error": str(e)}

# Main interface
col1, col2 = st.columns([2, 1])

with col1:
    st.header("📊 Database Overview")
    
    # Get database info
    db_info = get_database_info()
    
    if "error" in db_info:
        st.error(f"❌ Database Error: {db_info['error']}")
    else:
        # Database status
        if db_info["database_exists"]:
            st.success("✅ Database found and accessible")
            st.info(f"📍 **Location**: `{db_info['database_path']}`")
        else:
            st.error("❌ Database not found")
        
        # Collections info
        if db_info["collections"]:
            st.subheader("📚 Collections")
            for collection in db_info["collections"]:
                with st.expander(f"Collection: {collection['name']} ({collection['count']} documents)"):
                    col_details = get_collection_details(collection['name'])
                    
                    if "error" in col_details:
                        st.error(f"Error loading collection: {col_details['error']}")
                    else:
                        st.write(f"**Collection ID**: {collection['id']}")
                        st.write(f"**Document Count**: {col_details['count']}")
                        st.write(f"**Embedding Dimension**: {col_details['embedding_dimension']}")
                        
                        # Sample documents
                        if col_details['sample_docs']:
                            st.write("**Sample Documents**:")
                            for i, (doc, metadata) in enumerate(zip(col_details['sample_docs'][:3], col_details['sample_metadata'][:3])):
                                with st.container():
                                    st.write(f"Document {i+1}:")
                                    st.text_area(
                                        f"Content {i+1}",
                                        doc[:300] + "..." if len(doc) > 300 else doc,
                                        height=100,
                                        key=f"doc_{i}"
                                    )
                                    if metadata:
                                        st.json(metadata)
                                    st.markdown("---")
        else:
            st.warning("⚠️ No collections found in database")

with col2:
    st.header("🔧 Database Tools")
    
    # Refresh button
    if st.button("🔄 Refresh Database Info"):
        st.rerun()
    
    # Database statistics
    st.subheader("📈 Statistics")
    try:
        client = chromadb.PersistentClient(path=db_path)
        collection = client.get_collection('pdf_embeddings')
        
        # Get all metadata for analysis
        all_data = collection.get(include=['metadatas'])
        
        # Analyze sources
        sources = {}
        for metadata in all_data['metadatas']:
            if metadata and 'source' in metadata:
                source = metadata['source']
                sources[source] = sources.get(source, 0) + 1
        
        if sources:
            st.write("**Documents by Source:**")
            source_df = pd.DataFrame(list(sources.items()), columns=['Source', 'Chunks'])
            st.dataframe(source_df, use_container_width=True)
        
        # Total statistics
        st.metric("Total Chunks", len(all_data['ids']))
        st.metric("Unique Sources", len(sources))
        
    except Exception as e:
        st.error(f"Statistics error: {e}")
    
    # Database actions
    st.subheader("⚙️ Actions")
    
    if st.button("🗑️ Clear Database", type="secondary"):
        if st.checkbox("I understand this will delete all data"):
            try:
                import shutil
                shutil.rmtree(db_path)
                st.success("Database cleared!")
                st.rerun()
            except Exception as e:
                st.error(f"Error clearing database: {e}")
    
    if st.button("💾 Backup Database"):
        try:
            import shutil
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"./database_backup_{timestamp}"
            shutil.copytree(db_path, backup_path)
            st.success(f"Backup created: {backup_path}")
        except Exception as e:
            st.error(f"Backup error: {e}")

# Footer
st.markdown("---")
st.markdown("""
### 📖 How the Database Works

**ChromaDB** is a vector database that stores your PDF documents as:

1. **Text Chunks**: Your PDFs are split into manageable pieces
2. **Embeddings**: Each chunk is converted to a numerical vector using AI
3. **Metadata**: Source information and other details are stored
4. **Similarity Search**: When you ask questions, the system finds relevant chunks

**File Structure**:
- `./database/` - Main database folder
- `./database/chroma.sqlite3` - SQLite database file
- `./database/[uuid]/` - Collection data folders

**Access Methods**:
- **Web Interface**: This viewer (run with `streamlit run database_viewer.py`)
- **API**: Database health at `localhost:5001/health`
- **Direct**: Python scripts can access ChromaDB directly
""")
