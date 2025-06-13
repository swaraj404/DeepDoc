from sentence_transformers import SentenceTransformer
import chromadb
import google.generativeai as genai
import os

GOOGLE_API_KEY = "AIzaSyBToLypnjRLq96jpgt7Tz7bLVtsWN52tDg"  
genai.configure(api_key=GOOGLE_API_KEY)

genai.configure(api_key=GOOGLE_API_KEY)
gemini = genai.GenerativeModel("gemini-1.5-flash")

model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
chroma_client = chromadb.PersistentClient(path="./SE")
collection = chroma_client.get_or_create_collection(name="pdf_embeddings")

class AnswerRetriever:
    def __init__(self):
        self.model = model
        self.collection = collection

    def get_query_embedding(self, query):
        return self.model.encode([query], convert_to_tensor=True)

    def retrieve_chunks(self, query, marks):
        query_embedding = self.get_query_embedding(query)
        n_results = 3 if marks <= 2 else 7
        results = self.collection.query(
            query_embeddings=query_embedding.tolist(),
            n_results=n_results
        )
        return results.get('documents', [[]])[0]

    def format_prompt(self, query, chunks, marks):
        context = "\n---\n".join(chunks)
        if marks <= 2:
            prompt = f"""
You are an expert professor. Based on the context below, write a clear, concise and direct definition-style answer to the question.

Context:
{context}

Question: {query}
Answer:
"""
        else:
            prompt = f"""
You are an expert professor. Based on the context below, write a well-structured answer in bullet points. Avoid repeating lines. If the answer has steps, phases, or items, present them cleanly in bullets.

Context:
{context}

Question: {query}
Answer:
"""
        return prompt

    def get_gemini_answer(self, query, marks):
        chunks = self.retrieve_chunks(query, marks)
        print("\n\n🔍 Retrieved Chunks:")
        for i, chunk in enumerate(chunks):
            print(f"[{i+1}] {chunk}\n")
        prompt = self.format_prompt(query, chunks, marks)
        try:
            response = gemini.generate_content(prompt)
            print("\n✅ Answer:")
            print(response.text.strip())
            return response.text.strip()
        except Exception as e:
            print(f"\n❌ Error retrieving or generating answer: {e}")
            return None

if __name__ == "__main__":
    query = input("Enter your question: ")
    try:
        marks = int(input("How many marks is the question for? (e.g., 2, 5): "))
    except ValueError:
        marks = 2 

    retriever = AnswerRetriever()
    retriever.get_gemini_answer(query, marks)