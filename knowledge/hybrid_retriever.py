from config import HYBRID_RRF_K
from knowledge.vector_search import validate_query


class HybridRetriever:
    def __init__(self, database, vector_search):
        self.database = database
        self.vector_search = vector_search

    def search(self, query, limit=5):
        validate_query(query, limit)
        candidates = min(50, max(20, limit))
        keyword = self.database.search(query, candidates)
        semantic = self.vector_search.search(query, candidates)
        results = {}
        for method, rows in [('keyword', keyword), ('semantic', semantic)]:
            for rank, row in enumerate(rows, 1):
                item = results.setdefault(row['id'], {**row, 'score': 0.0, 'methods': []})
                item['score'] += 1 / (HYBRID_RRF_K + rank)
                item['methods'].append(method)
        return sorted(results.values(), key=lambda r: (-r['score'], r['id']))[:limit]
