import numpy as np

class VectorStore:
    def __init__(self):
        self.vectors = []
        self.texts = []

    def add(self, embedding, text):
        self.vectors.append(embedding)
        self.texts.append(text)

    def search(self, query_embedding, top_k=5):
        sims = np.dot(self.vectors, query_embedding)
        top_indices = sims.argsort()[-top_k:][::-1]
        return [self.texts[i] for i in top_indices]
