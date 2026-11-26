import numpy as np
from config import EMBEDDING_MODEL, EMBEDDING_DIMENSIONS, EMBEDDING_CACHE, CPU_THREADS

class EmbeddingEngine:
    def __init__(self, backend=None):
        self.backend = backend

    def embed(self, texts):
        if not texts or any(not isinstance(t, str) or not t.strip() for t in texts):
            raise ValueError("Nonempty text required.")
        if self.backend is None:
            from fastembed import TextEmbedding
            self.backend = TextEmbedding(model_name=EMBEDDING_MODEL,
                cache_dir=str(EMBEDDING_CACHE), threads=CPU_THREADS,
                local_files_only=True, providers=["CPUExecutionProvider"])
        vectors = np.asarray(list(self.backend.embed(texts, batch_size=16)), dtype=np.float32)
        if vectors.shape != (len(texts), EMBEDDING_DIMENSIONS) or not np.isfinite(vectors).all():
            raise ValueError("Invalid embedding output.")
        norms = np.linalg.norm(vectors, axis=1, keepdims=True)
        if not np.isfinite(norms).all() or (norms <= 0).any():
            raise ValueError("Invalid vector norm.")
        return vectors / norms
