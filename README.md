# 📄 PDF GPT - AI Powered PDF Question Answering

This project was developed as part of my 2nd year Computer Engineering studies.

PDF GPT allows users to upload PDF documents, processes their content into searchable chunks, and provides a user-friendly interface to ask questions about the document. It uses semantic search to retrieve relevant text and generates concise or detailed answers based on user preferences. The project includes both a Streamlit-based web interface and a Flask-based API, highlighting proficiency in full-stack development and AI integration.

Key Features
-PDF Processing: Extracts text from PDFs, tokenizes it into manageable chunks, and generates embeddings for semantic search.
-Semantic Search: Uses Sentence Transformers and ChromaDB to retrieve contextually relevant text based on user queries.
-Dynamic Answer Generation: Integrates Gemini AI to provide concise (definition-style) or detailed (bullet-point) answers based on a "marks" system.
-Streamlit Interface: A clean, interactive web interface for uploading PDFs, adjusting answer detail, and viewing conversation history.
-Flask API: A RESTful API for programmatic access to the question-answering system.
-Customizable Responses: Users can specify answer detail using a marks slider (2 for concise, 5 for detailed).
-Session Management: Maintains conversation history for a seamless user experience.

Learning Outcomes
This project demonstrates:
-AI and NLP: Integration of Sentence Transformers and Gemini AI for text processing and answer generation.
-Database Management: Use of ChromaDB for persistent storage of text embeddings.
-Web Development: Building user interfaces with Streamlit and APIs with Flask.
-Software Engineering: Modular code structure, error handling, and dependency management.
-Problem-Solving: Handling PDF text extraction, tokenization, and semantic search challenges.

Project Structure
-app.py: Streamlit application for the web interface, handling user interactions and displaying answers.
-app_v2.py: Flask API for programmatic question answering, suitable for integration with other systems.
-ingest.py: Processes PDF files, tokenizes text, generates embeddings, and stores them in ChromaDB.
-answer.py: Manages query embedding, chunk retrieval, and answer generation using Gemini AI.
-data2/: Directory for sample PDFs (e.g., Principles of Programming Languages - Technical.pdf).
-PPL/ and SE/: Directories for ChromaDB storage of embeddings.
-requirements.txt: Lists all Python dependencies.

Prerequisites
-Python: Version 3.8 or higher.
-Dependencies (install via requirements.txt):
-streamlit: For the web interface.
-pypdf: For PDF text extraction.
-nltk: For text tokenization.
-sentence-transformers: For generating text embeddings.
-chromadb: For storing and querying embeddings.
-google-generativeai: For interacting with the Gemini AI API.
-flask: For the RESTful API.
-Gemini API Key: Required for answer generation (see Configuration).
