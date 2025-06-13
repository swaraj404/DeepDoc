# 📄 PDF GPT - AI Powered PDF Question Answering

This project was developed as part of my 2nd year Computer Engineering studies.

PDF GPT helps users interact with PDFs and get answers by using AI models. Instead of manually searching through PDFs, you can simply upload a PDF or give its URL, ask your question, and get the answer along with the page number reference.

---

## 🚀 Problem Statement

Students and educators face difficulty finding answers from large textbooks and study material quickly. PDF GPT helps in answering queries directly from PDF documents using AI.

---

## 🎯 Solution Approach

- Upload or provide the URL of a PDF.
- The PDF is processed and converted into text.
- Semantic Search (using Universal Sentence Encoder) finds relevant parts.
- OpenAI GPT-3 (text-davinci-003) generates the final answer with page numbers.

---

## 🛠 Technologies Used

- Python
- FastAPI
- Gradio (User Interface)
- TensorFlow Hub (Universal Sentence Encoder)
- OpenAI GPT-3 (text-davinci-003)
- Docker & Docker Compose

---

## 🔑 Key Features

- Upload PDF or enter PDF URL.
- Ask any question related to the PDF content.
- Get accurate answers with page citations.
- User-friendly web interface built with Gradio.
- Easy to deploy using Docker.

---

## 💻 How It Works

1️⃣ Upload PDF or enter PDF URL.  
2️⃣ Enter your question.  
3️⃣ The system retrieves relevant content using Semantic Search.  
4️⃣ OpenAI GPT generates the answer.  
5️⃣ Answer includes proper page number references.
