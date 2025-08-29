import streamlit as st
from answer import AnswerRetriever


st.set_page_config(
    page_title="DeepDoc",
    page_icon="📚",
    layout="centered"
)

st.markdown("""
<stylewith st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 1rem 0;">
        <h2 style="color: #667eea; margin: 0;">⚙️ Control Panel</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # Question complexity settings
    st.markdown("### 🎯 Question Settings")
    marks = st.slider(
        "Answer Detail Level:",
        min_value=2,
        max_value=5,
        value=3,
        help="Higher values generate more detailed answers"
    )
    
    st.markdown("---")
    
    # PDF Upload Section
    st.markdown("### 📚 Upload Documents")
    uploaded_files = st.file_uploader(
        "Choose PDF files",
        type="pdf",
        accept_multiple_files=True,
        help="Upload one or more PDF files to add to your knowledge base"
    )
    
    if uploaded_files:
        if st.button("🚀 Process Documents", type="primary"):
            with st.spinner("Processing documents..."):
                # Process uploaded files
                success_count = 0
                for uploaded_file in uploaded_files:
                    try:
                        # Save uploaded file temporarily
                        import tempfile
                        import os
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                            tmp_file.write(uploaded_file.getvalue())
                            tmp_file_path = tmp_file.name
                        
                        # Process the file using ingest functionality
                        from ingest import DocumentProcessor
                        processor = DocumentProcessor()
                        processor.process_single_file(tmp_file_path, uploaded_file.name)
                        success_count += 1
                        
                        # Clean up
                        os.unlink(tmp_file_path)
                        
                    except Exception as e:
                        st.error(f"Error processing {uploaded_file.name}: {str(e)}")
                
                if success_count > 0:
                    st.success(f"✅ Successfully processed {success_count} document(s)!")
                    st.balloons()
                    st.rerun()
    
    st.markdown("---")
    
    # AI Provider Status
    st.markdown("### 🤖 AI Status")
    try:
        retriever = AnswerRetriever()
        provider = retriever.get_current_provider()
        
        col1, col2 = st.columns([1, 3])
        with col1:
            if provider == "local":
                st.markdown("🟢")
            else:
                st.markdown("🔵")
        with col2:
            if provider == "local":
                st.markdown("**Local AI**")
                st.caption("Offline mode")
            elif provider:
                st.markdown(f"**{provider.title()} AI**")
                st.caption("Online mode")
            else:
                st.markdown("**No AI**")
                st.caption("Not configured")
    except:
        st.markdown("🔴 **Status Unknown**")
    
    st.markdown("---")
    
    # Database Stats
    st.markdown("### 📊 Knowledge Base")
    try:
        import chromadb
        client = chromadb.PersistentClient(path='./database')
        collection = client.get_collection('pdf_embeddings')
        doc_count = collection.count()
        
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="margin: 0; color: #667eea;">{doc_count}</h3>
            <p style="margin: 0; color: #6c757d;">Document Chunks</p>
        </div>
        """, unsafe_allow_html=True)
        
        if doc_count > 0:
            st.success("📚 Knowledge base ready")
        else:
            st.warning("📭 No documents uploaded yet")
            
    except Exception as e:
        st.error("❌ Database unavailable")
    
    st.markdown("---")
    
    # Quick Actions
    st.markdown("### 🔧 Quick Actions")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄", help="Refresh status"):
            st.rerun()
    with col2:
        if st.button("🗑️", help="Clear chat"):
            st.session_state.history = []
            st.rerun()
    
    st.markdown("---")
    
    # Help section
    with st.expander("❓ Help & Tips"):
        st.markdown("""
        **Getting Started:**
        1. Upload PDF documents using the uploader above
        2. Ask questions about your documents
        3. Adjust detail level with the slider
        
        **Tips:**
        - Be specific in your questions
        - Upload multiple related documents for better answers
        - Higher detail levels provide more comprehensive responses
        
        **Sample Questions:**
        - "What is the main topic of this document?"
        - "Summarize the key points"
        - "Explain [specific concept] from the text"
        """)
    
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; opacity: 0.7; font-size: 0.8rem;">
        <p>💡 Powered by Local AI<br>🔒 Your data stays private</p>
    </div>
    """, unsafe_allow_html=True)rn Professional Styling */
    .main {
        padding: 0;
    }
    
    .main > div {
        padding: 1rem 2rem;
    }
    
    /* Header styling */
    .header-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem 0;
        margin: -1rem -2rem 2rem -2rem;
        color: white;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    .main-title {
        font-size: 3rem;
        font-weight: 700;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .subtitle {
        font-size: 1.2rem;
        margin-top: 0.5rem;
        opacity: 0.9;
    }
    
    /* Card styling */
    .feature-card {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
        margin: 1rem 0;
        border: 1px solid #e8ecef;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 35px rgba(0,0,0,0.15);
    }
    
    /* Upload area styling */
    .upload-area {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        color: white;
        margin: 1rem 0;
        box-shadow: 0 8px 25px rgba(240, 147, 251, 0.3);
    }
    
    /* Input styling */
    .stTextInput input {
        font-size: 16px;
        padding: 15px;
        border-radius: 25px;
        border: 2px solid #e8ecef;
        background: #f8f9fa;
        transition: all 0.3s ease;
    }
    
    .stTextInput input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        background: white;
    }
    
    /* Button styling */
    .stButton button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 12px 30px;
        border-radius: 25px;
        font-weight: 600;
        font-size: 16px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
    }
    
    /* File uploader styling */
    .stFileUploader > div {
        border: 2px dashed #667eea;
        border-radius: 15px;
        padding: 2rem;
        background: linear-gradient(135deg, #f8f9ff 0%, #e8ecff 100%);
        text-align: center;
    }
    
    /* Sidebar styling */
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 1rem;
    }
    
    /* Success/Error message styling */
    .stSuccess, .stError, .stWarning, .stInfo {
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    /* Chat message styling */
    .stChatMessage {
        border-radius: 15px;
        padding: 1rem;
        margin: 0.5rem 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    
    /* Metrics styling */
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        text-align: center;
        margin: 0.5rem 0;
        border-left: 4px solid #667eea;
    }
    
    /* Animation for loading */
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.7; }
        100% { opacity: 1; }
    }
    
    .loading {
        animation: pulse 1.5s infinite;
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .main-title {
            font-size: 2rem;
        }
        .header-container {
            padding: 1rem 0;
        }
    }
</style>
""", unsafe_allow_html=True)

if "history" not in st.session_state:
    st.session_state.history = []

with st.sidebar:
    st.header("⚙️ Settings")
    marks = st.slider(
        "Select marks for the question:",
        min_value=2,
        max_value=5,
        value=3,
        help="Higher marks will generate more detailed answers"
    )
    st.markdown("---")
    
    # Show AI provider status (lightweight check)
    try:
        retriever = AnswerRetriever()
        provider = retriever.get_current_provider()
        if provider == "local":
            st.success("🤖 Local AI")
        elif provider:
            st.info(f"🔗 {provider.title()} AI")
        else:
            st.warning("⚠️ No AI configured")
    except:
        st.warning("⚠️ AI status unknown")
    
    st.markdown("---")
    st.info("� Ask questions about your PDF documents")

st.markdown('<h1 class="main-title">📚 DeepDoc</h1>', unsafe_allow_html=True)
st.caption("Ask questions about your uploaded PDF content")

for entry in st.session_state.history:
    with st.chat_message(entry["role"]):
        st.markdown(entry["content"])

if prompt := st.chat_input("Type your question here..."):
    st.session_state.history.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant"):
        with st.spinner("🤖 Analyzing your question..."):
            try:
                retriever = AnswerRetriever()
                result = retriever.get_answer_with_sources(prompt, marks, include_sources=False)
                
                if result and result.get('success') and result.get('answer'):
                    answer = result['answer']
                    confidence = result.get('confidence', 0)
                    chunks_used = result.get('chunks_used', 0)
                    
                    # Display the answer
                    st.markdown(answer)
                    
                    # Show confidence and metadata
                    col1, col2 = st.columns(2)
                    with col1:
                        if confidence > 0:
                            confidence_color = "🟢" if confidence > 0.7 else "🟡" if confidence > 0.4 else "🔴"
                            st.caption(f"{confidence_color} Confidence: {confidence:.1%}")
                    with col2:
                        if chunks_used > 0:
                            st.caption(f"📄 Sources used: {chunks_used}")
                    
                    st.session_state.history.append({"role": "assistant", "content": answer})
                else:
                    error_msg = result.get('error', 'Unknown error occurred') if result else 'No response received'
                    st.error(f"❌ Sorry, I couldn't generate an answer: {error_msg}")
                    st.info("💡 Try rephrasing your question or asking about different topics from your documents.")
            except Exception as e:
                st.error(f"⚠️ An error occurred: {str(e)}")
                st.info("🔧 Please check if the documents are properly loaded and try again.")

if st.session_state.history and st.button("Clear Conversation History"):
    st.session_state.history = []
    st.rerun()