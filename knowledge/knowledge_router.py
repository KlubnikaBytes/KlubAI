import unicodedata
from knowledge.knowledge_manager import KnowledgeManager


def safe_display(value):
    return ''.join(c if c in '\n\t' or not unicodedata.category(c).startswith('C') else ' ' for c in str(value))


class KnowledgeRouter:
    def __init__(self, manager=None):
        self.manager = manager if manager is not None else KnowledgeManager()

    def route(self, message):
        parts = message.strip().split(maxsplit=1)
        if not parts or not parts[0].lower().startswith('/knowledge-'):
            return None
        command = parts[0].lower()
        arg = parts[1].strip() if len(parts) == 2 else ''
        if command == '/knowledge-help':
            return ('Knowledge commands (Phase 7D)\n/knowledge-info\n/knowledge-list\n'
                    '/knowledge-files\n/knowledge-add filename\n/knowledge-add-all\n'
                    '/knowledge-search words\n/knowledge-remove ID confirm\n'
                    '/knowledge-embed\n/knowledge-embedding-info\n'
                    '/knowledge-semantic query\n/knowledge-hybrid query\n/knowledge-retrieval-info')
        if command == '/knowledge-retrieval-info' and not arg:
            stats = self.manager.embedding_store().statistics()
            return ("Keyword: SQLite FTS5 / BM25\nSemantic: cosine similarity\nHybrid: reciprocal rank fusion\n"
                    f"Embedded chunks: {stats['indexed']}/{stats['total']}\nPending chunks: {stats['pending']}")
        if command in ('/knowledge-semantic', '/knowledge-hybrid'):
            if not arg:
                return f'Usage: {command} query'
            try:
                stats = self.manager.embedding_store().statistics()
                semantic = command == '/knowledge-semantic'
                results = self.manager.semantic_search(arg) if semantic else self.manager.hybrid_search(arg)
                label = 'Cosine similarity' if semantic else 'RRF score'
                lines = [f"Rank {i}: {safe_display(r['filename'])} | {safe_display(r['source_location'])}\n{label}: {r['score']:.6f}\n{safe_display(r['content'][:1500])}" for i, r in enumerate(results, 1)]
                response = '\n\n'.join(lines) or 'No matching knowledge found.'
                if stats['pending']:
                    response += f"\nWarning: {stats['pending']} chunks lack embeddings. Run /knowledge-embed."
                return response
            except Exception as error:
                return 'Retrieval failed: ' + safe_display(error)
        if command == '/knowledge-embedding-info' and not arg:
            stats = self.manager.embedding_store().statistics()
            return f"Embedding dimensions: 384\nTotal chunks: {stats['total']}\nEmbedded chunks: {stats['indexed']}\nPending chunks: {stats['pending']}"
        if command == '/knowledge-embed' and not arg:
            try:
                count = self.manager.embedding_store().build()
                return f"Generated embeddings: {count}"
            except Exception as error:
                return "Embedding failed: " + safe_display(error)
        if command == '/knowledge-files'  and not arg:
            return '\n'.join(safe_display(f['name']) for f in self.manager.list_files()) or 'No source documents.'
        if command == '/knowledge-add':
            if not arg:
                return 'Usage: /knowledge-add filename'
            try:
                result = self.manager.ingest(arg)
            except ValueError as error:
                return 'Import rejected: ' + safe_display(error)
            return f"Imported: {safe_display(result['filename'])} | ID: {result['id']} | Chunks: {result['chunks']}"
        if command == '/knowledge-add-all' and not arg:
            results = self.manager.ingest_all()
            lines = []
            for result in results:
                name = safe_display(result['filename'])
                if 'error' in result:
                    lines.append(f"Not imported: {name} | {safe_display(result['error'])}")
                else:
                    lines.append(f"Imported: {name} | ID: {result['id']} | Chunks: {result['chunks']}")
            return '\n'.join(lines) or 'No source documents.'
        if command == '/knowledge-info' and not arg:
            stats = self.manager.statistics()
            return f"Knowledge database: SQLite FTS5\nDocuments: {stats['documents']}\nChunks: {stats['chunks']}"
        if command == '/knowledge-list' and not arg:
            docs = self.manager.list_documents()
            return '\n'.join(f"{d['id']}: {safe_display(d['filename'])} ({d['chunk_count']} chunks)" for d in docs) or 'No indexed documents.'
        if command == '/knowledge-search':
            if not arg:
                return 'Usage: /knowledge-search words'
            results = self.manager.search(arg)
            return '\n\n'.join(f"Source: {safe_display(r['filename'])} | {safe_display(r['source_location'])}\n{safe_display(r['content'][:1500])}" for r in results) or 'No matching knowledge found.'
        if command == '/knowledge-remove':
            fields = arg.split()
            if len(fields) != 2 or not fields[0].isascii() or not fields[0].isdigit() or len(fields[0]) > 18 or fields[1] != 'confirm':
                return 'Usage: /knowledge-remove ID confirm'
            return 'Indexed document removed.' if self.manager.remove_document(int(fields[0])) else 'Document not found.'
        return 'Unknown or incomplete knowledge command. Use /knowledge-help.'
