# 🗄️ DeepDoc Database Guide

## Overview

DeepDoc uses **ChromaDB**, a modern vector database, to store and search through your PDF documents intelligently. This guide explains how the database works and how to interact with it.

## 🏗️ Database Architecture

### Core Components

1. **ChromaDB Vector Database**
   - Stores document chunks as high-dimensional vectors
   - Enables semantic similarity search
   - Persistent storage in `./database/` folder

2. **Document Processing Pipeline**
   ```
   PDF → Text Extraction → Chunking → Embeddings → ChromaDB
   ```

3. **Query Processing**
   ```
   User Question → Embedding → Similarity Search → Relevant Chunks → AI Answer
   ```

## 📁 File Structure

```
DeepDoc/
├── database/                    # Main database folder
│   ├── chroma.sqlite3          # SQLite metadata database
│   └── [collection-uuid]/      # Collection data folders
│       ├── data_level0.bin     # Vector index files
│       ├── header.bin          # Index headers
│       └── length.bin          # Document lengths
├── database_backup_*/          # Automatic backups
└── SE/                         # Legacy database (if exists)
```

## 🔍 Database Inspection Tools

### 1. Web Database Viewer
```bash
streamlit run database_viewer.py --server.port 8504
```
**Features:**
- Visual database overview
- Document content preview
- Statistics and analytics
- Backup/restore functionality

### 2. Command-Line Inspector
```bash
python db_inspector.py [command]
```

**Available Commands:**
- `info` - Database overview
- `details` - Collection details
- `sources` - List document sources
- `search "query"` - Search content
- `help` - Show help

**Examples:**
```bash
python db_inspector.py info
python db_inspector.py search "artificial intelligence"
python db_inspector.py sources
```

### 3. API Health Check
```bash
curl localhost:5001/health | python3 -m json.tool
```

## 📊 Current Database Status

**Your database contains:**
- 🗂️ **Collection**: `pdf_embeddings`
- 📄 **Documents**: 302 chunks
- 📚 **Sources**: 3 unique files
  - Final_HCI_Unit1.pptx: 83 chunks
  - HCI_Unit2_ppt_V3: 42 chunks  
  - CNS paper solution: 177 chunks

## 🔧 Database Operations

### Adding Documents
```bash
# Add new PDFs to the database
python ingest.py
# or via API
curl -X POST localhost:5001/upload -F "file=@document.pdf"
```

### Searching Content
```python
from answer import AnswerRetriever
retriever = AnswerRetriever()
chunks = retriever.retrieve_relevant_chunks("your question")
```

### Backup Database
```bash
# Automatic backup
cp -r ./database ./database_backup_$(date +%Y%m%d_%H%M%S)

# Or use the web interface backup button
```

### Clear Database
```python
import shutil
shutil.rmtree('./database')
```

## 🎯 How Vector Search Works

1. **Document Ingestion**:
   - PDFs are split into 500-character chunks
   - Each chunk is converted to a 384-dimensional vector using sentence-transformers
   - Vectors are stored with metadata (source, page, etc.)

2. **Query Processing**:
   - User question is converted to the same 384-dimensional space
   - ChromaDB finds the most similar vectors using cosine similarity
   - Top relevant chunks are retrieved for AI processing

3. **Similarity Threshold**:
   - Current threshold: 0.01 (very permissive)
   - Higher values = more strict matching
   - Lower values = more lenient matching

## 🔐 Database Security

- **Local Storage**: Database is stored locally, no cloud dependency
- **No External Access**: Database is only accessible from your machine
- **Backup Recommended**: Regular backups prevent data loss
- **No Sensitive Data**: Only stores document text, no personal information

## 🚀 Performance Optimization

### Current Settings
- **Embedding Model**: `sentence-transformers/all-MiniLM-L6-v2`
- **Chunk Size**: 500 characters with 50 character overlap
- **Max Chunks Retrieved**: Dynamic based on question complexity
- **Similarity Threshold**: 0.01

### Tuning Options
- Increase chunk overlap for better context
- Use larger embedding models for better accuracy
- Adjust similarity threshold for precision/recall balance

## 🛠️ Troubleshooting

### Database Not Found
```bash
# Check if database exists
ls -la ./database/

# Restore from backup
cp -r ./database_backup_* ./database
```

### No Documents Found
```bash
# Check collections
python db_inspector.py info

# Re-ingest documents
python ingest.py
```

### Low Similarity Scores
- Documents might not contain relevant information
- Try rephrasing your question
- Check if documents were processed correctly

### Performance Issues
- Database gets slower with more documents
- Consider periodic optimization
- Monitor disk space in `./database/`

## 📈 Monitoring

### Key Metrics to Watch
- **Document Count**: Should match your uploaded PDFs
- **Collection Health**: Should show as "healthy" in API
- **Disk Usage**: Database grows with more documents
- **Query Response Time**: Should be under 2 seconds

### Health Checks
```bash
# API health
curl localhost:5001/health

# Database inspector
python db_inspector.py info

# Web viewer
streamlit run database_viewer.py --server.port 8504
```

## 🔄 Maintenance Tasks

### Regular Maintenance
1. **Weekly Backups**: Use web interface or command line
2. **Disk Space Check**: Monitor `./database/` folder size
3. **Performance Testing**: Test query response times
4. **Document Updates**: Re-ingest if PDFs change

### Advanced Operations
```bash
# Database migration
python migrate.py

# Performance optimization
python optimize_database.py

# Index rebuilding (if needed)
python rebuild_index.py
```

---

## 🎓 Understanding Your Data

Your DeepDoc database currently contains educational materials:
- **HCI (Human-Computer Interaction)** content from PowerPoint presentations
- **CNS (Computer Network Security)** examination materials
- Processed into **302 searchable chunks** for intelligent Q&A

The system can answer questions about:
- HCI concepts and principles
- Computer network security topics
- Specific exam questions and solutions
- Cross-references between different materials

**Access your enhanced interface at**: http://localhost:8503
**Database viewer at**: http://localhost:8504
