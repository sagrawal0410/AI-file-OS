import numpy as np
import faiss
import logging
from file_scanner import scan_directory
from embedding_gen import get_document_embedding
DOCUMENTS = []
INDEX = None

def build_index(directory):
    global DOCUMENTS, INDEX
    logging.info("Scanning directory for documents...")
    DOCUMENTS=scan_directory(directory)
    if not DOCUMENTS:
        logging.info("No documents found")
        return
    embeddings_list=[]
    for doc in DOCUMENTS:
        embeddings_result=get_document_embedding(doc['text'])
        final_embeddings=embeddings_result.get('aggregated')
        if final_embeddings is not None:
            doc['embeddings']=final_embeddings
            embeddings_list.append(final_embeddings)
    if not embeddings_list:
        logging.info("No embeddings generated")
        return
    embeddings_np=np.array(embeddings_list).astype('float32')
    d=embeddings_np.shape[1]
    INDEX=faiss.IndexFlatL2(d)
    INDEX.add(embeddings_np)
    logging.info(f"FAISS index built with {len(DOCUMENTS)} documents")

def semantic_search(query, model, k=5):
    global INDEX, DOCUMENTS
    if INDEX is None:
        logging.info("Index is not built yet.")
        return []
    query_embedding = model.encode(query)
    query_embedding = np.array([query_embedding]).astype('float32')
    distances, indices = INDEX.search(query_embedding, k)
    results = []
    for dist, idx in zip(distances[0], indices[0]):
        if idx < len(DOCUMENTS):
            results.append({
                'path': DOCUMENTS[idx]['path'],
                'score': dist,
                'snippet': DOCUMENTS[idx]['text'][:200]  # first 200 characters as preview
            })
    return results