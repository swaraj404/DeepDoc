# � DeepDoc - Enhanced AI-Powered PDF Question Answering

> **Advanced document intelligence system with enterprise-grade features.**

DeepDoc is a comprehensive AI-powered application that transforms how you interact with PDF documents. Upload documents, ask questions, and get intelligent answers with source citations. Built with modern architecture, enhanced security, and production-ready deployment options.

---

## 🚀 Key Features

### Core Functionality
- **Smart PDF Processing**: Advanced text extraction with intelligent chunking and overlap
- **Semantic Search**: State-of-the-art sentence transformers with ChromaDB vector database
- **AI-Powered Answers**: Dynamic answer generation using Google's Gemini AI with confidence scoring
- **Source Attribution**: Detailed source citations with similarity scores and metadata

### Enhanced Interface
- **Modern Streamlit Web App**: Beautiful, responsive UI with chat interface and real-time feedback
- **RESTful API**: Comprehensive Flask API with rate limiting, caching, and documentation
- **File Upload Management**: Batch processing with progress tracking and error handling
- **Configuration Dashboard**: Real-time system statistics and health monitoring

### Production Features
- **Environment Configuration**: Secure environment variable management with validation
- **Docker Support**: Full containerization with Docker Compose for easy deployment
- **Redis Caching**: Optional caching layer for improved performance
- **Comprehensive Logging**: Structured logging with configurable levels
- **Health Checks**: Built-in monitoring and status endpoints
- **Backup System**: Automated database backup and recovery

---

## 🎯 Learning Outcomes & Technical Skills

### AI & Machine Learning
- **Natural Language Processing**: Sentence transformers, embedding generation, semantic similarity
- **Large Language Models**: Integration with Google Gemini AI, prompt engineering, response optimization
- **Vector Databases**: ChromaDB implementation, similarity search, metadata management

### Software Engineering
- **Clean Architecture**: Modular design, separation of concerns, dependency injection
- **Error Handling**: Comprehensive exception management, retry logic, graceful degradation
- **Configuration Management**: Environment variables, settings validation, deployment configurations

### Full-Stack Development
- **Frontend**: Modern Streamlit applications with custom CSS and responsive design
- **Backend**: Flask APIs with proper HTTP status codes, request validation, and documentation
- **Database**: Vector database management, data persistence, backup strategies

### DevOps & Deployment
- **Containerization**: Docker multi-stage builds, Docker Compose orchestration
- **Environment Management**: Development, staging, and production configurations
- **Monitoring**: Health checks, logging, performance metrics
- **Security**: API key management, rate limiting, CORS configuration

---

## 🗂️ Enhanced Project Structure

| File/Folder | Description |
| ------------ | ----------- |
| **Core Application** | |
| `app_improved.py` | Enhanced Streamlit web application with modern UI |
| `api_enhanced.py` | Production-ready Flask API with advanced features |
| `answer.py` | Improved answer retrieval with confidence scoring |
| `ingest.py` | Advanced PDF processing with smart chunking |
| **Configuration** | |
| `.env` / `.env.example` | Environment configuration files |
| `requirements.txt` | Comprehensive Python dependencies |
| `setup.sh` | Automated setup script |
| **Deployment** | |
| `Dockerfile` | Multi-stage Docker build configuration |
| `docker-compose.yml` | Full-stack deployment orchestration |
| `DEPLOYMENT.md` | Comprehensive deployment guide |
| **Data & Storage** | |
| `database/` | ChromaDB vector database storage |
| `logs/` | Application logs and monitoring |
| `backups/` | Automated database backups |

---

## ⚙️ Prerequisites

### System Requirements
- **Python 3.8+** (Python 3.11 recommended)
- **Memory**: Minimum 4GB RAM (8GB recommended for large documents)
- **Storage**: 2GB free space for dependencies and database

### Required API Keys
- **Google API Key**: Required for Gemini AI integration
  - Get from [Google AI Studio](https://makersuite.google.com/app/apikey)
  - Enable Generative AI API in Google Cloud Console

### Optional Dependencies
- **Docker & Docker Compose**: For containerized deployment
- **Redis**: For caching and performance optimization

---

## 🚀 Quick Start

### Option 1: Automated Setup (Recommended)
```bash
# Clone the repository
git clone <your-repo-url>
cd DeepDoc

# Run the setup script
./setup.sh

# Edit environment file with your API key
nano .env

# Activate virtual environment
source .venv/bin/activate

# Start the application
streamlit run app_improved.py
```

### Option 2: Manual Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Create environment file
cp .env.example .env

# Edit with your Google API key
nano .env

# Create directories
mkdir -p database logs backups

# Start the app
streamlit run app_improved.py
```

### Option 3: Docker Deployment
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f deepdoc-app

# Access at http://localhost:8501
```

---

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `GOOGLE_API_KEY` | Google Generative AI API key | - | ✅ |
| `DATABASE_PATH` | ChromaDB storage path | `./database` | |
| `COLLECTION_NAME` | Vector collection name | `pdf_embeddings` | |
| `SIMILARITY_THRESHOLD` | Minimum similarity for retrieval | `0.3` | |
| `MAX_CHUNK_SIZE` | Maximum chunk size in characters | `500` | |
| `LOG_LEVEL` | Logging level (DEBUG/INFO/WARNING/ERROR) | `INFO` | |

### Performance Tuning
```bash
# For large documents
export MAX_CHUNK_SIZE=800
export CHUNK_OVERLAP=100

# For high-traffic scenarios
export REDIS_HOST=localhost
export CACHE_SIZE=1000
```

---

## 📖 Usage Guide

### Web Interface
1. **Upload Documents**: Drag and drop PDF files or use the file browser
2. **Configure Settings**: Adjust question marks, context chunks, and source display
3. **Ask Questions**: Type questions in the chat interface
4. **Review Answers**: Get AI-generated answers with confidence scores and sources

### API Usage
```bash
# Upload a document
curl -X POST -F "files=@document.pdf" http://localhost:5000/upload

# Ask a question
curl -X POST http://localhost:5000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What is machine learning?", "marks": 5}'

# Search for relevant chunks
curl -X POST http://localhost:5000/search \
  -H "Content-Type: application/json" \
  -d '{"query": "neural networks", "max_chunks": 3}'
```

---

## � API Documentation

### Endpoints

| Endpoint | Method | Description |
|----------|---------|-------------|
| `/health` | GET | System health check |
| `/ask` | POST | Ask questions about documents |
| `/upload` | POST | Upload and process PDF files |
| `/search` | POST | Search for relevant document chunks |
| `/documents` | GET | List all documents in collection |
| `/stats` | GET | Get system statistics |

### Example Response
```json
{
  "success": true,
  "answer": "Machine learning is a subset of artificial intelligence...",
  "confidence": 0.85,
  "sources": [
    {
      "content_preview": "Machine learning algorithms can learn from data...",
      "similarity": 0.92,
      "metadata": {"source": "ai_textbook", "page": 15}
    }
  ]
}
```

---

## 🚢 Deployment Options

### Local Development
- Streamlit development server
- Flask development server
- SQLite-based ChromaDB

### Production Docker
- Multi-container setup with Docker Compose
- Redis caching
- Persistent volumes
- Health checks and monitoring

### Cloud Deployment
- **AWS**: ECS, EC2, or Lambda
- **Google Cloud**: Cloud Run, Compute Engine
- **Azure**: Container Instances, App Service

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions.

---

## 🧪 Testing

```bash
# Test installation
./setup.sh --test

# Test API endpoints
curl http://localhost:5000/health

# Test document processing
python -c "from ingest import ImprovedIngestDoc; print('✅ Import successful')"
```

---

## 📊 Performance & Monitoring

### Metrics
- Document processing time
- Query response time
- Memory usage
- API rate limits

### Monitoring
- Health check endpoints
- Application logs
- Error tracking
- Performance metrics

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 🆘 Support & Troubleshooting

### Common Issues
- **API Key Errors**: Ensure `GOOGLE_API_KEY` is set correctly
- **Memory Issues**: Reduce `MAX_CHUNK_SIZE` or increase system memory
- **Slow Performance**: Enable Redis caching and optimize chunk parameters

### Getting Help
- Check the [troubleshooting section](DEPLOYMENT.md#troubleshooting) in DEPLOYMENT.md
- Review application logs in the `logs/` directory
- Create an issue in the repository

### Resources
- [Google AI Studio](https://makersuite.google.com/)
- [ChromaDB Documentation](https://docs.trychroma.com/)
- [Streamlit Documentation](https://docs.streamlit.io/)

---

**Built with ❤️ for intelligent document processing**
pypdf
nltk
sentence-transformers
chromadb
google-generativeai
flask
