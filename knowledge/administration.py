"""Local knowledge administration; run with a single KlubAI process."""
import hashlib
import json
import sqlite3
from contextlib import closing
from pathlib import Path
from uuid import uuid4
from datetime import datetime, timezone
import numpy as np
from config import EMBEDDING_MODEL, EMBEDDING_DIMENSIONS

COMMANDS = {
    '/knowledge-status': 'Show database and embedding status',
    '/knowledge-detail ID': 'Show document metadata',
    '/knowledge-update ID': 'Replace indexed content from source',
    '/knowledge-sync': 'Preview source changes without modifying index',
    '/knowledge-reindex ID': 'Rebuild document chunks and embeddings',
    '/knowledge-reindex-all confirm': 'Rebuild all indexes',
    '/knowledge-duplicates': 'Find identical source files',
    '/knowledge-verify': 'Check database, FTS and vectors',
    '/knowledge-backup': 'Create local database backup',
    '/knowledge-backups': 'List local backups',
    '/knowledge-restore filename confirm': 'Restore backup (automatic safety backup)',
    '/knowledge-export': 'Export metadata as JSON',
    '/knowledge-clear confirm': 'Clear index (automatic safety backup)',
}

class KnowledgeAdministration:
    def __init__(self, manager):
        self.manager = manager
        self.database = manager.database
        self.directory = self.database.db_path.resolve().parent / 'backups'

    def detail(self, document_id):
        for doc in self.database.list_documents():
            if doc['id'] == document_id:
                return doc
        raise ValueError('Document not found.')

    def prepare(self, doc):
        ingestor = self.manager.ingestor
        path = ingestor.reader.validator.validate(doc['filename'])
        data = path.read_bytes()
        digest = hashlib.sha256(data).hexdigest()
        result = ingestor.reader.read(path.name)
        if hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            raise ValueError('Source changed during extraction.')
        chunks = ingestor.chunker.split(result['content'])
        if result['truncated'] or not chunks or not any(c.isalnum() for c in result['content']):
            raise ValueError('Source is empty or exceeds extraction limits.')
        return doc, digest, result['format'], len(data), chunks

    def replace(self, documents, embed=False):
        prepared = [self.prepare(doc) for doc in documents]
        store = self.manager.embedding_store()
        vectors = []
        for _, _, _, _, chunks in prepared:
            vectors.append(store.engine.embed([c[0] for c in chunks]) if embed else None)
        with self.database.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            for (doc, digest, fmt, size, chunks), batch in zip(prepared, vectors):
                current = db.execute('SELECT file_hash FROM knowledge_documents WHERE id=?', (doc['id'],)).fetchone()
                if current is None or current[0] != doc['file_hash']:
                    raise ValueError('Index changed; retry.')
                db.execute('UPDATE knowledge_documents SET file_hash=?,file_type=?,file_size=? WHERE id=?', (digest,fmt,size,doc['id']))
                db.execute('DELETE FROM knowledge_chunks WHERE document_id=?', (doc['id'],))
                for i,(content,location) in enumerate(chunks):
                    cid = db.execute('INSERT INTO knowledge_chunks(document_id,chunk_index,content,source_location) VALUES(?,?,?,?)',(doc['id'],i,content,location)).lastrowid
                    if batch is not None:
                        db.execute('INSERT INTO knowledge_embeddings VALUES(?,?,?,?)',(cid,EMBEDDING_MODEL,EMBEDDING_DIMENSIONS,batch[i].astype('<f4').tobytes()))
        return len(prepared)

    def source_hashes(self):
        validator = self.manager.ingestor.reader.validator
        return {f['name']:hashlib.sha256(validator.validate(f['name']).read_bytes()).hexdigest() for f in self.manager.list_files()}

    def sync(self):
        sources = self.source_hashes()
        indexed = {d['filename']:d['file_hash'] for d in self.database.list_documents()}
        return {'new':sorted(sources.keys()-indexed.keys()), 'missing_or_unreadable':sorted(indexed.keys()-sources.keys()), 'modified':sorted(n for n in sources.keys() & indexed.keys() if sources[n]!=indexed[n]), 'unchanged':sorted(n for n in sources.keys() & indexed.keys() if sources[n]==indexed[n])}

    def duplicates(self):
        groups = {}
        for name,digest in self.source_hashes().items():
            groups.setdefault(digest,[]).append(name)
        return [names for names in groups.values() if len(names)>1]

    @staticmethod
    def verify_connection(db):
        if [r[0] for r in db.execute('PRAGMA integrity_check')] != ['ok'] or db.execute('PRAGMA foreign_key_check').fetchone():
            raise ValueError('SQLite integrity check failed.')
        db.execute("INSERT INTO knowledge_chunks_fts(knowledge_chunks_fts,rank) VALUES('integrity-check',1)")
        for dims, blob in db.execute('SELECT dimensions,vector FROM knowledge_embeddings'):
            v = np.frombuffer(blob,dtype='<f4')
            if dims != EMBEDDING_DIMENSIONS or v.size != dims or not np.isfinite(v).all() or not np.isclose(np.linalg.norm(v),1,atol=1e-5):
                raise ValueError('Invalid stored vector.')
        if db.execute('SELECT id FROM knowledge_documents WHERE NOT EXISTS (SELECT 1 FROM knowledge_chunks WHERE document_id=knowledge_documents.id)').fetchone():
            raise ValueError('Document without chunks.')

    def verify(self):
        self.manager.embedding_store()
        with self.database.connect() as db:
            self.verify_connection(db)
        return 'SQLite, foreign keys, FTS5 and vector integrity checks passed. Missing embeddings are reported separately.'

    def new_path(self, suffix):
        self.directory.mkdir(parents=True,exist_ok=True)
        return self.directory / (datetime.now(timezone.utc).strftime('knowledge_%Y%m%d_%H%M%S_')+uuid4().hex+suffix)

    def backup(self):
        self.manager.embedding_store()
        path = self.new_path('.sqlite3')
        try:
            with self.database.connect() as source, closing(sqlite3.connect(path)) as target:
                source.backup(target)
                self.verify_connection(target)
                target.commit()
        except BaseException:
            path.unlink(missing_ok=True)
            raise
        return path.name

    def backups(self):
        return sorted(p.name for p in self.directory.glob('knowledge_*.sqlite3') if p.is_file() and not p.is_symlink())

    def restore(self, name):
        if name not in self.backups() or Path(name).name != name:
            raise ValueError('Select a listed backup filename.')
        path = self.directory / name
        # Validate in memory; never execute FTS integrity writes on the backup itself.
        with closing(sqlite3.connect(path.resolve().as_uri()+'?mode=ro',uri=True)) as source, closing(sqlite3.connect(':memory:')) as copy:
            source.backup(copy)
            with self.database.connect() as live:
                schema = lambda db: sorted(tuple(r) for r in db.execute("SELECT type,name,sql FROM sqlite_master WHERE name NOT LIKE 'sqlite_%'"))
                if schema(copy) != schema(live):
                    raise ValueError('Backup schema does not match current knowledge database.')
            self.verify_connection(copy)
            copy.commit()
            safety = self.backup()
            with self.database.connect() as live:
                copy.backup(live)
        return safety

    def clear(self):
        safety = self.backup()
        with self.database.connect() as db:
            db.execute('DELETE FROM knowledge_documents')
        return safety

    def export(self):
        path = self.new_path('.json')
        path.write_text(json.dumps(self.database.list_documents(),indent=2,ensure_ascii=False),encoding='utf-8')
        return path.name

    def route(self, command, arg):
        commands = {k.split()[0]:k for k in COMMANDS}
        if command not in commands:
            return None
        usage = 'Usage: '+commands[command]
        if command in ('/knowledge-detail','/knowledge-update','/knowledge-reindex'):
            if not arg.isascii() or not arg.isdigit() or len(arg)>18:
                return usage
            doc = self.detail(int(arg))
            if command == '/knowledge-detail': return json.dumps(doc,indent=2,ensure_ascii=False)
            self.replace([doc],embed=command=='/knowledge-reindex')
            return 'Document updated. '+('Embeddings rebuilt.' if command=='/knowledge-reindex' else 'Run /knowledge-embed to index updated chunks.')
        if command == '/knowledge-restore':
            name,sep,confirm = arg.rpartition(' ')
            if not sep or confirm!='confirm': return usage
            return 'Restored. Previous index backup: '+self.restore(name)
        if command in ('/knowledge-clear','/knowledge-reindex-all'):
            if arg!='confirm': return usage
            if command=='/knowledge-clear': return 'Index cleared. Source files retained. Backup: '+self.clear()
            return f'Reindexed documents: {self.replace(self.database.list_documents(),embed=True)}'
        if arg: return usage
        if command=='/knowledge-status': return json.dumps({**self.database.statistics(),**self.manager.embedding_store().statistics()},indent=2)
        if command=='/knowledge-sync': return json.dumps(self.sync(),indent=2,ensure_ascii=False)
        if command=='/knowledge-duplicates': return json.dumps(self.duplicates(),indent=2,ensure_ascii=False)
        if command=='/knowledge-verify': return self.verify()
        if command=='/knowledge-backup': return 'Backup created: '+self.backup()
        if command=='/knowledge-backups': return '\n'.join(self.backups()) or 'No backups.'
        if command=='/knowledge-export': return 'Metadata exported: '+self.export()
