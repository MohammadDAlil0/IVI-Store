from sentence_transformers import SentenceTransformer
import numpy as np

def generate_embedding_local(sentences):
    model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
    embeddings = model.encode(sentences)
    return np.array(embeddings)
  
  
