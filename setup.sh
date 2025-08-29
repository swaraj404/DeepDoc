#!/bin/bash

# DeepDoc Setup Script
# This script helps set up the DeepDoc environment

set -e

echo "🚀 DeepDoc Setup Script"
echo "======================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if Python is installed
check_python() {
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
        print_status "Python $PYTHON_VERSION found"
    else
        print_error "Python 3 is not installed. Please install Python 3.8 or higher."
        exit 1
    fi
}

# Check if pip is installed
check_pip() {
    if command -v pip3 &> /dev/null; then
        print_status "pip3 found"
    else
        print_error "pip3 is not installed. Please install pip3."
        exit 1
    fi
}

# Create virtual environment
create_venv() {
    if [ ! -d ".venv" ]; then
        echo "Creating virtual environment..."
        python3 -m venv .venv
        print_status "Virtual environment created"
    else
        print_status "Virtual environment already exists"
    fi
}

# Activate virtual environment
activate_venv() {
    source .venv/bin/activate
    print_status "Virtual environment activated"
}

# Install requirements
install_requirements() {
    echo "Installing Python dependencies..."
    pip install --upgrade pip
    pip install -r requirements.txt
    print_status "Dependencies installed"
}

# Create directories
create_directories() {
    echo "Creating necessary directories..."
    mkdir -p database logs backups data
    print_status "Directories created"
}

# Setup environment file
setup_env() {
    if [ ! -f ".env" ]; then
        if [ -f ".env.example" ]; then
            cp .env.example .env
            print_warning "Environment file created from template"
            print_warning "Please edit .env and add your GOOGLE_API_KEY"
        else
            cat > .env << EOF
# DeepDoc Environment Configuration
GOOGLE_API_KEY=your_google_api_key_here
GEMINI_MODEL=gemini-1.5-flash
DATABASE_PATH=./database
COLLECTION_NAME=pdf_embeddings
SENTENCE_MODEL=sentence-transformers/all-MiniLM-L6-v2
SIMILARITY_THRESHOLD=0.3
MAX_RETRIES=3
RETRY_DELAY=1
LOG_LEVEL=INFO
MAX_FILE_SIZE=10485760
ALLOWED_EXTENSIONS=pdf
MAX_CHUNK_SIZE=500
CHUNK_OVERLAP=50
SECRET_KEY=dev-key-change-in-production
ALLOWED_HOSTS=localhost,127.0.0.1
CACHE_SIZE=100
MAX_CONCURRENT_REQUESTS=10
EOF
            print_status "Environment file created"
            print_warning "Please edit .env and add your GOOGLE_API_KEY"
        fi
    else
        print_status "Environment file already exists"
    fi
}

# Download NLTK data
download_nltk_data() {
    echo "Downloading NLTK data..."
    python3 -c "import nltk; nltk.download('punkt')" 2>/dev/null || true
    print_status "NLTK data downloaded"
}

# Test installation
test_installation() {
    echo "Testing installation..."
    
    # Test imports
    python3 -c "
import sys
try:
    import streamlit
    import chromadb
    import google.generativeai
    import sentence_transformers
    import pypdf
    import nltk
    import flask
    print('✅ All required packages imported successfully')
except ImportError as e:
    print(f'❌ Import error: {e}')
    sys.exit(1)
" || {
        print_error "Import test failed. Please check the installation."
        return 1
    }
    
    print_status "Installation test passed"
}

# Check for Docker
check_docker() {
    if command -v docker &> /dev/null; then
        print_status "Docker found"
        if command -v docker-compose &> /dev/null; then
            print_status "Docker Compose found"
        else
            print_warning "Docker Compose not found. Install it for containerized deployment."
        fi
    else
        print_warning "Docker not found. Install it for containerized deployment."
    fi
}

# Main setup function
main() {
    echo "Starting DeepDoc setup..."
    echo
    
    # Check prerequisites
    check_python
    check_pip
    check_docker
    
    echo
    
    # Setup environment
    create_venv
    activate_venv
    install_requirements
    create_directories
    setup_env
    download_nltk_data
    
    echo
    
    # Test installation
    test_installation
    
    echo
    print_status "Setup completed successfully!"
    echo
    echo "📝 Next steps:"
    echo "1. Edit .env file and add your GOOGLE_API_KEY"
    echo "2. Run: source .venv/bin/activate"
    echo "3. Start the app: streamlit run app_improved.py"
    echo "   OR start the API: python api_enhanced.py"
    echo
    echo "📖 For deployment options, see DEPLOYMENT.md"
    echo
    
    # Check if API key is set
    if grep -q "your_google_api_key_here" .env 2>/dev/null; then
        print_warning "Remember to set your GOOGLE_API_KEY in the .env file!"
    fi
}

# Parse command line arguments
case "${1:-}" in
    --help|-h)
        echo "DeepDoc Setup Script"
        echo
        echo "Usage: $0 [options]"
        echo
        echo "Options:"
        echo "  --help, -h     Show this help message"
        echo "  --test         Run tests only"
        echo "  --env          Setup environment file only"
        echo "  --docker       Check Docker installation"
        echo
        echo "No arguments: Run full setup"
        exit 0
        ;;
    --test)
        activate_venv 2>/dev/null || true
        test_installation
        exit 0
        ;;
    --env)
        setup_env
        exit 0
        ;;
    --docker)
        check_docker
        exit 0
        ;;
    "")
        main
        ;;
    *)
        print_error "Unknown option: $1"
        print_error "Use --help for usage information"
        exit 1
        ;;
esac
