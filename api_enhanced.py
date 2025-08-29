import os
import logging
import tempfile
import redis
from datetime import datetime
from typing import Dict, List, Optional
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge
from dotenv import load_dotenv
from answer import ImprovedAnswerRetriever
from ingest import ImprovedIngestDoc
from functools import wraps

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=getattr(logging, os.getenv('LOG_LEVEL', 'INFO')),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Configuration
app.config.update({
    'MAX_CONTENT_LENGTH': int(os.getenv('MAX_FILE_SIZE', 16 * 1024 * 1024)),  # 16MB
    'SECRET_KEY': os.getenv('SECRET_KEY', 'dev-key-change-in-production'),
    'UPLOAD_FOLDER': tempfile.mkdtemp(),
})

# Enable CORS
CORS(app, origins=os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(','))

# Initialize Redis for caching (optional)
try:
    redis_client = redis.Redis(
        host=os.getenv('REDIS_HOST', 'localhost'),
        port=int(os.getenv('REDIS_PORT', 6379)),
        db=int(os.getenv('REDIS_DB', 0)),
        decode_responses=True
    )
    redis_client.ping()
    logger.info("Redis connected successfully")
except Exception as e:
    logger.warning(f"Redis not available: {e}")
    redis_client = None

# Global instances
retriever = None
ingestor = None

def init_components():
    """Initialize retriever and ingestor"""
    global retriever, ingestor
    try:
        if not retriever:
            retriever = ImprovedAnswerRetriever()
            logger.info("Answer retriever initialized")
        
        if not ingestor:
            ingestor = ImprovedIngestDoc()
            logger.info("Document ingestor initialized")
            
    except Exception as e:
        logger.error(f"Failed to initialize components: {e}")
        raise

def rate_limit(max_requests: int = 60, window: int = 60):
    """Rate limiting decorator"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if redis_client:
                client_ip = request.remote_addr
                key = f"rate_limit:{client_ip}:{f.__name__}"
                
                try:
                    current = redis_client.get(key)
                    if current is None:
                        redis_client.setex(key, window, 1)
                    elif int(current) >= max_requests:
                        return jsonify({
                            'error': 'Rate limit exceeded',
                            'message': f'Maximum {max_requests} requests per {window} seconds'
                        }), 429
                    else:
                        redis_client.incr(key)
                except Exception as e:
                    logger.warning(f"Rate limiting error: {e}")
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def cache_response(ttl: int = 300):
    """Cache response decorator"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if redis_client and request.method == 'POST':
                cache_key = f"cache:{f.__name__}:{hash(str(request.get_json()))}"
                
                try:
                    cached = redis_client.get(cache_key)
                    if cached:
                        return jsonify(eval(cached))
                except Exception as e:
                    logger.warning(f"Cache retrieval error: {e}")
            
            result = f(*args, **kwargs)
            
            if redis_client and request.method == 'POST' and result:
                try:
                    redis_client.setex(cache_key, ttl, str(result.get_data(as_text=True)))
                except Exception as e:
                    logger.warning(f"Cache storage error: {e}")
            
            return result
        return decorated_function
    return decorator

@app.before_request
def startup():
    """Initialize components on startup"""
    if not hasattr(startup, 'initialized'):
        try:
            init_components()
            logger.info("DeepDoc API started successfully")
            startup.initialized = True
        except Exception as e:
            logger.error(f"Failed to start API: {e}")

@app.errorhandler(413)
def too_large(e):
    return jsonify({
        'error': 'File too large',
        'message': f'Maximum file size is {app.config["MAX_CONTENT_LENGTH"]} bytes'
    }), 413

@app.errorhandler(500)
def internal_error(e):
    logger.error(f"Internal error: {e}")
    return jsonify({
        'error': 'Internal server error',
        'message': 'An unexpected error occurred'
    }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        status = {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'components': {
                'retriever': retriever is not None,
                'ingestor': ingestor is not None,
                'redis': redis_client is not None
            }
        }
        
        if retriever:
            status['database'] = retriever.get_collection_info()
        
        return jsonify(status), 200
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/ask', methods=['POST'])
@rate_limit(max_requests=30, window=60)
@cache_response(ttl=300)
def ask_question():
    """Answer questions based on uploaded documents"""
    try:
        data = request.get_json()
        
        if not data or 'question' not in data:
            return jsonify({
                'error': 'Missing required field',
                'message': 'Please provide a question in the request body'
            }), 400
        
        question = data['question'].strip()
        if not question:
            return jsonify({
                'error': 'Empty question',
                'message': 'Question cannot be empty'
            }), 400
        
        # Extract optional parameters
        marks = data.get('marks', 3)
        include_sources = data.get('include_sources', False)  # Changed to False by default
        max_chunks = data.get('max_chunks', None)
        
        # Validate parameters
        if not isinstance(marks, int) or marks < 1 or marks > 10:
            marks = 3
        
        if max_chunks and (not isinstance(max_chunks, int) or max_chunks < 1):
            max_chunks = None
        
        # Get answer
        result = retriever.get_answer_with_sources(
            question, 
            marks=marks,
            include_sources=include_sources,
            max_chunks=max_chunks
        )
        
        # Format response
        response = {
            'success': True,
            'question': question,
            'answer': result['answer'],
            'confidence': result.get('confidence', 0),
            'chunks_used': result.get('chunks_used', 0),
            'timestamp': datetime.now().isoformat()
        }
        
        if include_sources and result.get('sources'):
            response['sources'] = result['sources']
        
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Error processing question: {e}")
        return jsonify({
            'success': False,
            'error': 'Processing error',
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/upload', methods=['POST'])
@rate_limit(max_requests=10, window=300)  # More restrictive for uploads
def upload_documents():
    """Upload and process PDF documents"""
    try:
        if 'files' not in request.files:
            return jsonify({
                'error': 'No files provided',
                'message': 'Please provide PDF files to upload'
            }), 400
        
        files = request.files.getlist('files')
        if not files or all(f.filename == '' for f in files):
            return jsonify({
                'error': 'No files selected',
                'message': 'Please select at least one PDF file'
            }), 400
        
        results = {'successful': [], 'failed': []}
        
        for file in files:
            if file and file.filename.lower().endswith('.pdf'):
                try:
                    # Save file temporarily
                    filename = secure_filename(file.filename)
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                        file.save(tmp_file.name)
                        tmp_path = tmp_file.name
                    
                    # Process the file
                    document_id = os.path.splitext(filename)[0]
                    success = ingestor.save_document_to_db(tmp_path, document_id)
                    
                    # Clean up
                    os.unlink(tmp_path)
                    
                    if success:
                        results['successful'].append(filename)
                    else:
                        results['failed'].append(filename)
                        
                except Exception as e:
                    logger.error(f"Error processing file {file.filename}: {e}")
                    results['failed'].append(file.filename)
            else:
                results['failed'].append(file.filename if file else 'Unknown file')
        
        # Get updated collection info
        collection_info = retriever.get_collection_info() if retriever else {}
        
        return jsonify({
            'success': True,
            'results': results,
            'collection_info': collection_info,
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except RequestEntityTooLarge:
        return jsonify({
            'error': 'File too large',
            'message': f'Maximum file size is {app.config["MAX_CONTENT_LENGTH"]} bytes'
        }), 413
    except Exception as e:
        logger.error(f"Upload error: {e}")
        return jsonify({
            'success': False,
            'error': 'Upload error',
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/documents', methods=['GET'])
@rate_limit(max_requests=100, window=60)
def list_documents():
    """List all documents in the collection"""
    try:
        collection_info = retriever.get_collection_info()
        
        # Try to get sample documents to show what's available
        sample_data = {}
        try:
            if retriever.collection.count() > 0:
                results = retriever.collection.get(limit=10)
                if results.get('metadatas'):
                    sources = set()
                    for metadata in results['metadatas']:
                        if metadata and 'source' in metadata:
                            sources.add(metadata['source'])
                    sample_data['available_documents'] = list(sources)
        except Exception as e:
            logger.warning(f"Could not retrieve sample documents: {e}")
        
        return jsonify({
            'success': True,
            'collection_info': collection_info,
            'sample_data': sample_data,
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Error listing documents: {e}")
        return jsonify({
            'success': False,
            'error': 'Listing error',
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/search', methods=['POST'])
@rate_limit(max_requests=50, window=60)
@cache_response(ttl=600)
def search_documents():
    """Search for relevant document chunks without generating answers"""
    try:
        data = request.get_json()
        
        if not data or 'query' not in data:
            return jsonify({
                'error': 'Missing required field',
                'message': 'Please provide a query in the request body'
            }), 400
        
        query = data['query'].strip()
        if not query:
            return jsonify({
                'error': 'Empty query',
                'message': 'Query cannot be empty'
            }), 400
        
        max_chunks = data.get('max_chunks', 5)
        
        # Get relevant chunks
        chunks = retriever.retrieve_relevant_chunks(query, max_chunks=max_chunks)
        
        return jsonify({
            'success': True,
            'query': query,
            'chunks': chunks,
            'total_found': len(chunks),
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Search error: {e}")
        return jsonify({
            'success': False,
            'error': 'Search error',
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/stats', methods=['GET'])
@rate_limit(max_requests=200, window=60)
@cache_response(ttl=60)
def get_stats():
    """Get system statistics"""
    try:
        stats = {
            'collection_info': retriever.get_collection_info() if retriever else {},
            'system_info': {
                'redis_available': redis_client is not None,
                'components_initialized': {
                    'retriever': retriever is not None,
                    'ingestor': ingestor is not None
                }
            },
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify({
            'success': True,
            'stats': stats
        }), 200
        
    except Exception as e:
        logger.error(f"Stats error: {e}")
        return jsonify({
            'success': False,
            'error': 'Stats error',
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/clear-cache', methods=['POST'])
@rate_limit(max_requests=10, window=60)
def clear_cache():
    """Clear Redis cache"""
    try:
        if redis_client:
            redis_client.flushall()
            return jsonify({
                'success': True,
                'message': 'Cache cleared successfully',
                'timestamp': datetime.now().isoformat()
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': 'Redis cache not available',
                'timestamp': datetime.now().isoformat()
            }), 404
            
    except Exception as e:
        logger.error(f"Cache clear error: {e}")
        return jsonify({
            'success': False,
            'error': 'Cache clear error',
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/docs', methods=['GET'])
def api_documentation():
    """API documentation"""
    docs = {
        'title': 'DeepDoc API',
        'version': '2.0',
        'description': 'Enhanced PDF Question-Answering API',
        'endpoints': {
            '/health': {
                'method': 'GET',
                'description': 'Health check endpoint',
                'response': 'System status and component health'
            },
            '/ask': {
                'method': 'POST',
                'description': 'Ask questions about uploaded documents',
                'parameters': {
                    'question': 'Required string - The question to ask',
                    'marks': 'Optional integer (1-10) - Question difficulty level',
                    'include_sources': 'Optional boolean - Include source information',
                    'max_chunks': 'Optional integer - Maximum context chunks to use'
                }
            },
            '/upload': {
                'method': 'POST',
                'description': 'Upload and process PDF documents',
                'parameters': {
                    'files': 'Required file array - PDF files to upload'
                }
            },
            '/documents': {
                'method': 'GET',
                'description': 'List documents in the collection'
            },
            '/search': {
                'method': 'POST',
                'description': 'Search for relevant document chunks',
                'parameters': {
                    'query': 'Required string - Search query',
                    'max_chunks': 'Optional integer - Maximum chunks to return'
                }
            },
            '/stats': {
                'method': 'GET',
                'description': 'Get system statistics'
            }
        }
    }
    
    return jsonify(docs), 200

if __name__ == '__main__':
    # Development server
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    port = int(os.getenv('PORT', 5000))
    host = os.getenv('HOST', '0.0.0.0')
    
    logger.info(f"Starting DeepDoc API on {host}:{port} (debug={debug_mode})")
    app.run(host=host, port=port, debug=debug_mode)
