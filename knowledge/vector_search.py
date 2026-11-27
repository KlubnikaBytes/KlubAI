import heapq
import numpy as np
from config import EMBEDDING_MODEL, EMBEDDING_DIMENSIONS, SEMANTIC_MIN_SCORE


def validate_query(query, limit):
    if not isinstance(query, str) or not query.strip() or len(query) > 1000 or not any(c.isalnum() for c in query):
        raise ValueError("Enter a searchable query of up to 1000 characters.")
    if not isinstance(limit, int) or not 1 <= limit <= 50:
        raise ValueError("Result limit must be between 1 and 50.")


class VectorSearch:
    def __init__(self, store):
        self.store = store

    def search(self, query, limit=5, min_score=SEMANTIC_MIN_SCORE):
        validate_query(query, limit)
        if not -1 <= min_score <= 1:
            raise ValueError("Invalid similarity threshold.")
        if not self.store.statistics()['indexed']:
            return []
        vector = self.store.engine.embed([query])[0]
        heap = []
        with self.store.database.connect() as db:
            rows = db.execute("""SELECT c.id,c.document_id,d.filename,c.chunk_index,
                c.content,c.source_location,e.vector,e.dimensions
                FROM knowledge_embeddings e JOIN knowledge_chunks c ON c.id=e.chunk_id
                JOIN knowledge_documents d ON d.id=c.document_id
                WHERE e.model=? ORDER BY c.id""", (EMBEDDING_MODEL,))
            for row in rows:
                stored = np.frombuffer(row['vector'], dtype='<f4')
                if row['dimensions'] != EMBEDDING_DIMENSIONS or stored.size != EMBEDDING_DIMENSIONS or not np.isfinite(stored).all() or not np.isclose(np.linalg.norm(stored), 1, atol=1e-5):
                    raise ValueError("Invalid stored embedding; rebuild the affected document.")
                score = float(np.clip(stored @ vector, -1, 1))
                if score < min_score:
                    continue
                result = dict(row)
                del result['vector'], result['dimensions']
                result['score'] = score
                item = (score, -row['id'], result)
                if len(heap) < limit:
                    heapq.heappush(heap, item)
                elif item[:2] > heap[0][:2]:
                    heapq.heapreplace(heap, item)
        return [item[2] for item in sorted(heap, reverse=True)]
