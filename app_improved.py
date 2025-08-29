import streamlit as st
import os
import tempfile
import logging
from datetime import datetime
from typing import Optional
from answer import ImprovedAnswerRetriever, AnswerRetriever
from ingest import ImprovedIngestDoc, Ingestdoc

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="DeepDoc - Enhanced PDF Q&A",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
<style>
    .stTextInput input {
        font-size: 16px;
        padding: 12px;
        border-radius: 8px;
    }
    .stButton button {
        width: 100%;
        padding: 10px;
        font-weight: bold;
        background: linear-gradient(45deg, #4CAF50, #45a049);
        color: white;
        border-radius: 8px;
        border: none;
        transition: all 0.3s;
    }
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    .chat-message {
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .user-message {
        background-color: #e3f2fd;
        border-left: 4px solid #2196F3;
    }
    .assistant-message {
        background-color: #f1f8e9;
        border-left: 4px solid #4CAF50;
    }
    .error-message {
        background-color: #ffebee;
        border-left: 4px solid #f44336;
        color: #c62828;
    }
    .success-message {
        background-color: #e8f5e8;
        border-left: 4px solid #4caf50;
        color: #2e7d32;
    }
    .info-box {
        background-color: #f5f5f5;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #ddd;
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #4CAF50;
    }
    .source-card {
        background: #f8f9fa;
        padding: 0.8rem;
        border-radius: 6px;
        margin: 0.5rem 0;
        border: 1px solid #e9ecef;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
def init_session_state():
    """Initialize session state variables"""
    if "history" not in st.session_state:
        st.session_state.history = []
    if "retriever" not in st.session_state:
        st.session_state.retriever = None
    if "collection_info" not in st.session_state:
        st.session_state.collection_info = {}
    if "uploaded_files" not in st.session_state:
        st.session_state.uploaded_files = []

def load_retriever():
    """Load the answer retriever with error handling"""
    try:
        if st.session_state.retriever is None:
            with st.spinner("Initializing AI system..."):
                st.session_state.retriever = ImprovedAnswerRetriever()
                st.session_state.collection_info = st.session_state.retriever.get_collection_info()
            
        return st.session_state.retriever
    except Exception as e:
        st.error(f"Failed to initialize the system: {str(e)}")
        st.info("Please check your environment variables and database setup.")
        return None

def process_uploaded_file(uploaded_file, ingestor) -> bool:
    """Process a single uploaded PDF file"""
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            tmp_file.write(uploaded_file.read())
            tmp_file_path = tmp_file.name
        
        # Process the file
        document_id = os.path.splitext(uploaded_file.name)[0]
        success = ingestor.save_document_to_db(tmp_file_path, document_id)
        
        # Clean up temporary file
        os.unlink(tmp_file_path)
        
        return success
        
    except Exception as e:
        logger.error(f"Error processing uploaded file: {e}")
        return False

def display_answer_with_sources(result: dict, show_sources: bool = True):
    """Display answer with optional sources in a structured format"""
    # Main answer
    st.markdown("### 📝 Answer")
    
    # Only show confidence if sources are enabled (for advanced users)
    if show_sources:
        st.markdown(f"**Confidence:** {result.get('confidence', 0):.1%}")
    
    # Display the answer prominently
    st.markdown(f"**{result['answer']}**")
    
    # Sources section - only if enabled
    if show_sources and result.get('sources'):
        st.markdown("### 📚 Sources Used")
        
        for i, source in enumerate(result['sources']):
            with st.expander(f"Source {i+1} (Similarity: {source['similarity']:.2f})"):
                st.text(source['content_preview'])
                
                # Show metadata if available
                metadata = source.get('metadata', {})
                if metadata.get('source'):
                    st.caption(f"📄 Document: {metadata['source']}")
                if metadata.get('chunk_index') is not None:
                    st.caption(f"📍 Section: {metadata['chunk_index'] + 1}")
    elif not show_sources:
        # Just show a simple note that sources are available
        st.caption("💡 Enable 'Show Sources' in the sidebar to see source documents")

def main():
    """Main application function"""
    init_session_state()
    
    # Header
    st.title("📚 DeepDoc - Enhanced PDF Q&A System")
    st.markdown("Ask questions about your uploaded PDF documents with AI-powered answers")
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # AI Provider Status
        ai_provider = os.getenv('AI_PROVIDER', 'openai').lower()
        provider_icons = {
            'openai': '🤖',
            'google': '🟢', 
            'anthropic': '🟣',
            'local': '🏠'
        }
        provider_names = {
            'openai': 'OpenAI GPT',
            'google': 'Google Gemini',
            'anthropic': 'Anthropic Claude',
            'local': 'Local AI (No API Key)'
        }
        
        st.info(f"{provider_icons.get(ai_provider, '🤖')} **AI Provider:** {provider_names.get(ai_provider, ai_provider.title())}")
        
        if ai_provider == 'local':
            st.success("✅ Running offline - No API key required!")
        
        st.markdown("---")
        
        # Question settings
        marks = st.slider(
            "Question Marks:",
            min_value=1,
            max_value=10,
            value=3,
            help="Higher marks generate more detailed answers"
        )
        
        max_chunks = st.slider(
            "Max Context Chunks:",
            min_value=1,
            max_value=15,
            value=5,
            help="Maximum number of relevant text chunks to use"
        )
        
        include_sources = st.checkbox(
            "Show Sources",
            value=False,  # Changed to False - sources hidden by default
            help="Display source information with answers"
        )
        
        st.markdown("---")
        
        # File upload section
        st.header("📄 Upload Documents")
        uploaded_files = st.file_uploader(
            "Choose PDF files",
            type=['pdf'],
            accept_multiple_files=True,
            help="Upload PDF files to add to your knowledge base"
        )
        
        if uploaded_files:
            if st.button("Process Uploaded Files"):
                ingestor = ImprovedIngestDoc()
                progress_bar = st.progress(0)
                
                successful = []
                failed = []
                
                for i, uploaded_file in enumerate(uploaded_files):
                    progress_bar.progress((i + 1) / len(uploaded_files))
                    
                    with st.spinner(f"Processing {uploaded_file.name}..."):
                        if process_uploaded_file(uploaded_file, ingestor):
                            successful.append(uploaded_file.name)
                            st.session_state.uploaded_files.append(uploaded_file.name)
                        else:
                            failed.append(uploaded_file.name)
                
                # Update collection info
                if st.session_state.retriever:
                    st.session_state.collection_info = st.session_state.retriever.get_collection_info()
                
                # Show results
                if successful:
                    st.success(f"✅ Successfully processed: {', '.join(successful)}")
                if failed:
                    st.error(f"❌ Failed to process: {', '.join(failed)}")
        
        st.markdown("---")
        
        # System information
        st.header("📊 System Status")
        
        # Load retriever and show collection info
        retriever = load_retriever()
        if retriever and st.session_state.collection_info:
            info = st.session_state.collection_info
            if 'error' not in info:
                st.metric("Total Documents", info.get('unique_documents', 0))
                st.metric("Total Chunks", info.get('total_chunks', 0))
                st.text(f"Database: {info.get('database_path', 'N/A')}")
                st.text(f"Collection: {info.get('collection_name', 'N/A')}")
        
        # Show uploaded files in current session
        if st.session_state.uploaded_files:
            st.subheader("📋 Recently Uploaded")
            for file_name in st.session_state.uploaded_files[-5:]:  # Show last 5
                st.text(f"• {file_name}")
        
        # Environment check
        st.markdown("**Environment:**")
        ai_provider = os.getenv('AI_PROVIDER', 'openai').lower()
        
        if ai_provider == 'local':
            st.text("🏠 Local AI: ✅ Active")
        elif ai_provider == 'openai':
            openai_key_status = "✅" if os.getenv('OPENAI_API_KEY') and os.getenv('OPENAI_API_KEY') != 'your_openai_api_key_here' else "❌"
            st.text(f"🤖 OpenAI Key: {openai_key_status}")
        elif ai_provider == 'google':
            google_key_status = "✅" if os.getenv('GOOGLE_API_KEY') else "❌"
            st.text(f"🟢 Google Key: {google_key_status}")
        elif ai_provider == 'anthropic':
            anthropic_key_status = "✅" if os.getenv('ANTHROPIC_API_KEY') else "❌"
            st.text(f"🟣 Anthropic Key: {anthropic_key_status}")

    
    # Main content area
    if not load_retriever():
        st.error("⚠️ System not available. Please check your configuration.")
        st.stop()
    
    # Display chat history
    for entry in st.session_state.history:
        if entry["role"] == "user":
            with st.chat_message("user"):
                st.markdown(entry["content"])
        else:
            with st.chat_message("assistant"):
                if "result" in entry:
                    display_answer_with_sources(entry["result"], include_sources)
                else:
                    st.markdown(entry["content"])
    
    # Chat input
    if prompt := st.chat_input("Type your question here..."):
        # Add user message to history
        st.session_state.history.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate and display assistant response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    result = st.session_state.retriever.get_answer_with_sources(
                        prompt, 
                        marks=marks, 
                        include_sources=include_sources,
                        max_chunks=max_chunks
                    )
                    
                    # Display the result
                    display_answer_with_sources(result, include_sources)
                    
                    # Add to history
                    st.session_state.history.append({
                        "role": "assistant", 
                        "result": result,
                        "content": result['answer']
                    })
                    
                except Exception as e:
                    error_msg = f"Sorry, I encountered an error: {str(e)}"
                    st.error(error_msg)
                    st.session_state.history.append({
                        "role": "assistant", 
                        "content": error_msg
                    })
    
    # Action buttons
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("🗑️ Clear Chat"):
            st.session_state.history = []
            st.rerun()
    
    with col2:
        if st.button("🔄 Refresh System"):
            st.session_state.retriever = None
            st.session_state.collection_info = {}
            st.rerun()
    
    with col3:
        if st.button("📊 Show Stats"):
            if st.session_state.retriever:
                stats = st.session_state.retriever.get_collection_info()
                st.json(stats)

if __name__ == "__main__":
    main()
