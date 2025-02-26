from sentence_transformers import SentenceTransformer
from config import CHUNK_SIZE, OVERLAP
import numpy as np

model = SentenceTransformer('all-MiniLM-L6-v2')

def split_text_into_chunks(text, chunk_size=CHUNK_SIZE, overlap=OVERLAP):
    words = text.split()
    chunks = []
    start = 0
    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunk = " ".join(words[start:end])
        chunks.append(chunk)
        # Move start pointer: subtract the overlap to ensure chunks share some context.
        start += chunk_size - overlap  
    return chunks

# Example usage:

def get_document_embedding(text):
    chunks=split_text_into_chunks(text)
    embeddings=[]
    embeddings=[model.encode(chunk) for chunk in chunks]
    result = {"embeddings": embeddings, "chunks": chunks}
    aggregated_embedding=np.mean(embeddings, axis=0)
    result["aggregated"]=aggregated_embedding
    return result