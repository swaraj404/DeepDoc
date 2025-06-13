# 📄 PDF GPT - AI Powered PDF Question Answering

> **Developed as part of my 2nd year Computer Engineering studies.**

PDF GPT is an AI-powered application that allows users to upload PDF documents and ask questions directly based on their content. It processes PDFs into searchable chunks, uses semantic search to retrieve relevant information, and generates concise or detailed answers powered by Gemini AI. The project demonstrates full-stack development, AI integration, and natural language processing.

---

## 🚀 Key Features

- **PDF Processing**: Extracts and tokenizes text into manageable chunks for analysis.
- **Semantic Search**: Uses Sentence Transformers with ChromaDB to retrieve contextually relevant content.
- **Dynamic Answer Generation**: Generates concise (definition-style) or detailed (bullet-point) answers based on user-selected marks.
- **Streamlit Web Interface**: User-friendly interface to upload PDFs, adjust answer detail, and interact via chat.
- **Flask API**: RESTful API to access the system programmatically.
- **Session Management**: Maintains conversation history for seamless interaction.

---

## 🎯 Learning Outcomes

- **AI & NLP**: Integration of Sentence Transformers and Gemini AI for answer generation.
- **Database Management**: ChromaDB for embedding storage and retrieval.
- **Full-Stack Development**: Web UI with Streamlit, backend API with Flask.
- **Software Engineering**: Clean modular code, error handling, and configuration management.
- **Problem-Solving**: Efficient PDF processing, semantic search optimization, and API integration.

---

## 🗂️ Project Structure

| File/Folder | Description |
| ------------ | ----------- |
| `app.py` | Streamlit web app |
| `app_v2.py` | Flask REST API |
| `ingest.py` | PDF processing & embedding generation |
| `answer.py` | Query handling & answer generation |
| `data2/` | Sample PDFs (e.g., *Principles of Programming Languages*) |
| `PPL/` & `SE/` | ChromaDB embedding storage |
| `requirements.txt` | Python dependencies |

---

## ⚙️ Prerequisites

- **Python 3.8+**
- Required packages (install via `requirements.txt`):

```bash
streamlit
pypdf
nltk
sentence-transformers
chromadb
google-generativeai
flask
