from rag.embeddings.embedder import embed

def retrieve(query, vector_store, k=5):
    q_emb = embed([query])[0]
    return vector_store.search(q_emb, top_k=k)
