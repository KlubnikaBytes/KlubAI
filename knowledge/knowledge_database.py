import re
import sqlite3
from contextlib import contextmanager
from pathlib import Path

from config import KNOWLEDGE_DATABASE_PATH


class KnowledgeDatabase:
    def __init__(self, db_path=KNOWLEDGE_DATABASE_PATH):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as db:
            db.executescript('''
                CREATE TABLE IF NOT EXISTS knowledge_documents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    filename TEXT NOT NULL UNIQUE,
                    file_hash TEXT NOT NULL UNIQUE,
                    file_type TEXT NOT NULL,
                    file_size INTEGER NOT NULL CHECK(file_size >= 0),
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
                CREATE TABLE IF NOT EXISTS knowledge_chunks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    document_id INTEGER NOT NULL REFERENCES knowledge_documents(id) ON DELETE CASCADE,
                    chunk_index INTEGER NOT NULL,
                    content TEXT NOT NULL,
                    source_location TEXT NOT NULL,
                    UNIQUE(document_id, chunk_index)
                );
                CREATE VIRTUAL TABLE IF NOT EXISTS knowledge_chunks_fts USING fts5(
                    content, content='knowledge_chunks', content_rowid='id'
                );
                CREATE TRIGGER IF NOT EXISTS knowledge_chunk_insert AFTER INSERT ON knowledge_chunks BEGIN
                    INSERT INTO knowledge_chunks_fts(rowid, content) VALUES(new.id, new.content);
                END;
                CREATE TRIGGER IF NOT EXISTS knowledge_chunk_delete AFTER DELETE ON knowledge_chunks BEGIN
                    INSERT INTO knowledge_chunks_fts(knowledge_chunks_fts, rowid, content) VALUES('delete', old.id, old.content);
                END;
                CREATE TRIGGER IF NOT EXISTS knowledge_chunk_update AFTER UPDATE ON knowledge_chunks BEGIN
                    INSERT INTO knowledge_chunks_fts(knowledge_chunks_fts, rowid, content) VALUES('delete', old.id, old.content);
                    INSERT INTO knowledge_chunks_fts(rowid, content) VALUES(new.id, new.content);
                END;
            ''')

    @contextmanager
    def connect(self):
        db = sqlite3.connect(str(self.db_path), timeout=10)
        db.row_factory = sqlite3.Row
        try:
            db.execute('PRAGMA foreign_keys = ON')
            yield db
            db.commit()
        except BaseException:
            db.rollback()
            raise
        finally:
            db.close()

    def add_document(self, filename, file_hash, file_type, file_size, chunks):
        if not filename.strip() or len(filename) > 255:
            raise ValueError('Invalid document name.')
        if not re.fullmatch(r'[0-9a-f]{64}', file_hash):
            raise ValueError('Invalid SHA-256 hash.')
        if not 1 <= len(chunks) <= 10000:
            raise ValueError('Expected 1 to 10000 chunks.')
        for content, location in chunks:
            if not content.strip() or len(content) > 10000 or len(location) > 500:
                raise ValueError('Invalid chunk content or location.')
        with self.connect() as db:
            try:
                cursor = db.execute('INSERT INTO knowledge_documents(filename,file_hash,file_type,file_size) VALUES(?,?,?,?)', (filename,file_hash,file_type,file_size))
            except sqlite3.IntegrityError as exc:
                raise ValueError('Duplicate document name/hash or invalid metadata.') from exc
            document_id = cursor.lastrowid
            db.executemany('INSERT INTO knowledge_chunks(document_id,chunk_index,content,source_location) VALUES(?,?,?,?)', ((document_id,i,content,location) for i,(content,location) in enumerate(chunks)))
            return document_id

    def list_documents(self):
        with self.connect() as db:
            return [dict(row) for row in db.execute('SELECT d.*, COUNT(c.id) AS chunk_count FROM knowledge_documents d LEFT JOIN knowledge_chunks c ON c.document_id=d.id GROUP BY d.id ORDER BY d.id')]

    def statistics(self):
        with self.connect() as db:
            return dict(db.execute('SELECT (SELECT COUNT(*) FROM knowledge_documents) AS documents, (SELECT COUNT(*) FROM knowledge_chunks) AS chunks').fetchone())

    def search(self, query, limit=5):
        if len(query) > 1000 or not 1 <= limit <= 50:
            raise ValueError('Search limit exceeded.')
        words = re.findall(r'[^\W_]+', query, flags=re.UNICODE)[:32]
        if not words:
            raise ValueError('Enter searchable words.')
        expression = ' OR '.join('"' + word + '"' for word in words)
        with self.connect() as db:
            rows = db.execute('''SELECT c.id, c.document_id, d.filename, c.chunk_index,
                c.content, c.source_location, bm25(knowledge_chunks_fts) AS score
                FROM knowledge_chunks_fts JOIN knowledge_chunks c ON c.id=knowledge_chunks_fts.rowid
                JOIN knowledge_documents d ON d.id=c.document_id
                WHERE knowledge_chunks_fts MATCH ? ORDER BY score, c.id LIMIT ?''', (expression,limit))
            return [dict(row) for row in rows]

    def remove_document(self, document_id):
        with self.connect() as db:
            return db.execute('DELETE FROM knowledge_documents WHERE id=?', (document_id,)).rowcount > 0
