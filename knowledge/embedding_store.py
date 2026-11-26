import numpy as np
from config import EMBEDDING_MODEL, EMBEDDING_DIMENSIONS
from knowledge.embedding_engine import EmbeddingEngine

class EmbeddingStore:
    def __init__(self, database, engine=None):
        self.database = database
        self.engine = engine if engine is not None else EmbeddingEngine()
        with database.connect() as db:
            db.execute("""CREATE TABLE IF NOT EXISTS knowledge_embeddings (
                chunk_id INTEGER NOT NULL REFERENCES knowledge_chunks(id) ON DELETE CASCADE,
                model TEXT NOT NULL, dimensions INTEGER NOT NULL CHECK(dimensions=384),
                vector BLOB NOT NULL CHECK(length(vector)=1536),
                PRIMARY KEY(chunk_id, model))""")
            db.execute("""CREATE TRIGGER IF NOT EXISTS invalidate_embedding AFTER UPDATE OF content ON knowledge_chunks
                BEGIN DELETE FROM knowledge_embeddings WHERE chunk_id=old.id; END""")

    def statistics(self):
        with self.database.connect() as db:
            total = db.execute("SELECT COUNT(*) FROM knowledge_chunks").fetchone()[0]
            indexed = db.execute("SELECT COUNT(*) FROM knowledge_embeddings WHERE model=?", (EMBEDDING_MODEL,)).fetchone()[0]
        return dict(total=total, indexed=indexed, pending=total-indexed)

    def build(self):
        created = 0
        while True:
            with self.database.connect() as db:
                rows = db.execute("""SELECT c.id,c.content FROM knowledge_chunks c
                    WHERE NOT EXISTS (SELECT 1 FROM knowledge_embeddings e WHERE e.chunk_id=c.id AND e.model=?)
                    ORDER BY c.id LIMIT 16""", (EMBEDDING_MODEL,)).fetchall()
            if not rows:
                return created
            vectors = self.engine.embed([r['content'] for r in rows])
            with self.database.connect() as db:
                for row, vector in zip(rows, vectors):
                    cursor = db.execute("""INSERT OR IGNORE INTO knowledge_embeddings(chunk_id,model,dimensions,vector)
                        SELECT id,?,?,? FROM knowledge_chunks WHERE id=? AND content=?""",
                        (EMBEDDING_MODEL, EMBEDDING_DIMENSIONS, vector.astype('<f4').tobytes(), row['id'], row['content']))
                    created += cursor.rowcount
