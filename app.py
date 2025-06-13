import streamlit as st
from answer import AnswerRetriever


st.set_page_config(
    page_title="DeepDoc",
    page_icon="📚",
    layout="centered"
)

st.markdown("""
<style>
    .stTextInput input {
        font-size: 16px;
        padding: 12px;
    }
    .stButton button {
        width: 100%;
        padding: 10px;
        font-weight: bold;
        background-color: #4CAF50;
        color: white;
    }
    .stMarkdown {
        font-size: 16px;
    }
    .sidebar .sidebar-content {
        background-color: #f0f2f6;
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
    st.info("This system uses Gemini AI and ChromaDB to answer questions based on your PDF content.")

st.title("📚 DeepDoc")
st.caption("Ask questions about your uploaded PDF content")

for entry in st.session_state.history:
    with st.chat_message(entry["role"]):
        st.markdown(entry["content"])

if prompt := st.chat_input("Type your question here..."):
    st.session_state.history.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant"):
        with st.spinner("Analyzing your question..."):
            try:
                retriever = AnswerRetriever()
                answer = retriever.get_gemini_answer(prompt, marks)
                
                if answer:
                    st.markdown(answer)
                    st.session_state.history.append({"role": "assistant", "content": answer})
                else:
                    st.error("Sorry, I couldn't generate an answer. Please try a different question.")
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")

if st.session_state.history and st.button("Clear Conversation History"):
    st.session_state.history = []
    st.rerun()