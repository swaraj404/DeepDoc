# 📄 PDF GPT - AI Powered PDF Question Answering

This project was developed as part of my 2nd year Computer Engineering studies.

PDF GPT allows users to upload PDF documents, processes their content into searchable chunks, and provides a user-friendly interface to ask questions about the document. It uses semantic search to retrieve relevant text and generates concise or detailed answers based on user preferences. The project includes both a Streamlit-based web interface and a Flask-based API, highlighting proficiency in full-stack development and AI integration.

Key Features





PDF Processing: Extracts text from PDFs, tokenizes it into manageable chunks, and generates embeddings for semantic search.



Semantic Search: Uses Sentence Transformers and ChromaDB to retrieve contextually relevant text based on user queries.



Dynamic Answer Generation: Integrates Gemini AI to provide concise (definition-style) or detailed (bullet-point) answers based on a "marks" system.



Streamlit Interface: A clean, interactive web interface for uploading PDFs, adjusting answer detail, and viewing conversation history.



Flask API: A RESTful API for programmatic access to the question-answering system.



Customizable Responses: Users can specify answer detail using a marks slider (2 for concise, 5 for detailed).



Session Management: Maintains conversation history for a seamless user experience.

Learning Outcomes

This project demonstrates:





AI and NLP: Integration of Sentence Transformers and Gemini AI for text processing and answer generation.



Database Management: Use of ChromaDB for persistent storage of text embeddings.



Web Development: Building user interfaces with Streamlit and APIs with Flask.



Software Engineering: Modular code structure, error handling, and dependency management.



Problem-Solving: Handling PDF text extraction, tokenization, and semantic search challenges.

Project Structure





app.py: Streamlit application for the web interface, handling user interactions and displaying answers.



app_v2.py: Flask API for programmatic question answering, suitable for integration with other systems.



ingest.py: Processes PDF files, tokenizes text, generates embeddings, and stores them in ChromaDB.



answer.py: Manages query embedding, chunk retrieval, and answer generation using Gemini AI.



data2/: Directory for sample PDFs (e.g., Principles of Programming Languages - Technical.pdf).



PPL/ and SE/: Directories for ChromaDB storage of embeddings.



requirements.txt: Lists all Python dependencies.

Prerequisites





Python: Version 3.8 or higher.



Dependencies (install via requirements.txt):





streamlit: For the web interface.



pypdf: For PDF text extraction.



nltk: For text tokenization.



sentence-transformers: For generating text embeddings.



chromadb: For storing and querying embeddings.



google-generativeai: For interacting with the Gemini AI API.



flask: For the RESTful API.



Gemini API Key: Required for answer generation (see Configuration).

Installation





Clone the Repository:

git clone https://github.com/<your-username>/deepdoc.git
cd deepdoc



Set Up a Virtual Environment:

python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate



Install Dependencies:

pip install -r requirements.txt



Download NLTK Data:

python -c "import nltk; nltk.download('punkt')"



Set Up Gemini API Key:





Obtain a Gemini API key from Google's API Console.



Replace the GOOGLE_API_KEY in answer.py and app_v2.py with your key:

GOOGLE_API_KEY = "your-api-key"



Alternatively, set it as an environment variable:

export GOOGLE_API_KEY="your-api-key"

Usage

Running the Streamlit Web App





Start the Streamlit server:

streamlit run app.py



Open your browser and go to http://localhost:8501.



Use the interface to:





Upload a PDF or use the sample PDF in data2/.



Adjust the marks slider (2–5) to control answer detail.



Type a question in the chat input to receive answers.



Clear conversation history if needed.

Running the Flask API





Start the Flask server:

python app_v2.py



Send a POST request to http://localhost:5000/ask with a JSON payload:

{
    "question": "What is object-oriented programming?",
    "context": "Optional additional context"
}

Example using curl:

curl -X POST -H "Content-Type: application/json" -d '{"question":"What is object-oriented programming?"}' http://localhost:5000/ask

Ingesting PDFs





Process a PDF to store its embeddings in ChromaDB:

python ingest.py



To use a different PDF, update the path in ingest.py:

store.save_embeddings_to_db("path/to/your/pdf.pdf")

Configuration





ChromaDB Storage:





Embeddings are stored in ./PPL (for ingestion) and ./SE (for retrieval). Ensure these directories exist and are writable.



Note: The project uses two separate ChromaDB paths due to modular design; ensure consistency or merge them if needed.



Marks System:





Marks ≤ 2: Short, definition-style answers.



Marks > 2: Detailed, bullet-point answers for comprehensive responses.



PDF Processing:





PDFs are split into chunks of ~300 characters, ignoring short lines (<30 characters) and questions.



Only text-based PDFs are supported; scanned PDFs require OCR preprocessing.

Example Usage





Upload a PDF: Use the sample Principles of Programming Languages - Technical.pdf in data2/.



Ingest the PDF:

python ingest.py



Ask Questions:





Via Streamlit: Open http://localhost:8501, set marks to 3, and ask, "What are the principles of programming languages?"



Via API: Send a POST request with {"question": "What are the principles of programming languages?"}.



View Responses:





Concise (marks=2): A short definition.



Detailed (marks=5): A bullet-point list with key points from the PDF.

Technical Details





PDF Processing: Uses pypdf to extract text and nltk for tokenization, ensuring robust handling of document structure.



Embedding Generation: Employs sentence-transformers/all-MiniLM-L6-v2 for lightweight, efficient embeddings.



Vector Search: ChromaDB stores embeddings and retrieves the top 3 (marks ≤ 2) or 7 (marks > 2) relevant chunks.



Answer Generation: Gemini AI (gemini-1.5-flash) generates answers based on retrieved chunks and a custom prompt.



Web Interface: Streamlit provides a responsive UI with a sidebar for settings and a chat-like interface for questions.



API: Flask offers a lightweight endpoint for integration with other applications.

Challenges Overcome





PDF Parsing: Handled inconsistent PDF formats by filtering irrelevant lines and optimizing chunk sizes.



Semantic Search: Balanced retrieval accuracy and performance using Sentence Transformers and ChromaDB.



API Integration: Managed Gemini API rate limits and error handling for reliable answer generation.



User Experience: Designed an intuitive interface with session management for seamless interaction.

Future Improvements





Support for scanned PDFs using OCR.



Integration with additional AI models for comparison.



Enhanced UI with real-time PDF previews and highlighting of retrieved chunks.



Optimization of embedding storage for larger PDFs.



Authentication for the Flask API to secure access.
