
from pypdf import PdfReader
import nltk
from sentence_transformers import SentenceTransformer
import chromadb
import re

nltk.download("punkt")
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

class Ingestdoc:
    def __init__(self):
        self.pdf_url = None

    def pdf_loader(self, pdf_url):
        load_pdf = PdfReader(pdf_url)
        text = ""
        for page_num, page in enumerate(load_pdf.pages):
            text += page.extract_text() + f"\n[PAGE {page_num+1}]\n"
        return text

    def tokenize_pdf(self, pdf_path):
        text = self.pdf_loader(pdf_path)
        if text:
            lines = text.split("\n")
            chunks = []
            current_chunk = ""
            for line in lines:
                stripped = line.strip()
                if not stripped:
                    continue
                if stripped.endswith("?") or len(stripped) < 30:
                    continue
                if re.match(r"^(\*|-|•|\d+[\.\)])\s+", stripped):
                    current_chunk += "\n" + stripped
                else:
                    current_chunk += " " + stripped
                if len(current_chunk) > 300:
                    chunks.append(current_chunk.strip())
                    current_chunk = ""
            if current_chunk:
                chunks.append(current_chunk.strip())
            return chunks
        return []

    def embedd_doc(self, chunks):
        return model.encode(chunks, convert_to_tensor=True)

    def save_embeddings_to_db(self, pdf_path):
        chroma_client = chromadb.PersistentClient(path="./PPL")
        collection = chroma_client.get_or_create_collection(name="pdf_embeddings")
        chunks = self.tokenize_pdf(pdf_path)
        embeddings = self.embedd_doc(chunks)

        if embeddings is not None and chunks:
            for i, chunk in enumerate(chunks):
                collection.add(
                    ids=[f"chunk_{i}"],
                    documents=[chunk],
                    embeddings=[embeddings[i].tolist()]
                )
            print("PDF stored successfully in ChromaDB.")
        else:
            print("Failed to store PDF embeddings.")

if __name__ == "__main__":
    store = Ingestdoc()
    store.save_embeddings_to_db("data2/Principles of Programming Languages - Technical.pdf") 