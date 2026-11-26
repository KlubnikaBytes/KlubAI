from config import RAG_MAX_CHUNKS, RAG_TEMPERATURE
from knowledge.context_builder import ContextBuilder
from knowledge.vector_search import validate_query
from knowledge.knowledge_router import safe_display

class RAGEngine:
    def __init__(self, engine, manager):
        self.engine = engine
        self.manager = manager
        self.builder = ContextBuilder(engine)

    def answer(self, question):
        validate_query(question, RAG_MAX_CHUNKS)
        if not self.engine.is_loaded():
            raise RuntimeError('Local model is not loaded.')
        rows = self.manager.hybrid_search(question, limit=15)
        # Require semantic support, not merely a common keyword match.
        rows = [row for row in rows if 'semantic' in row.get('methods', [])]
        messages, sources = self.builder.build(question, rows)
        if not sources:
            yield 'The available knowledge does not contain enough relevant evidence.'
            return
        pending = self.manager.embedding_store().statistics()['pending']
        if pending:
            yield f'Warning: {pending} chunks lack embeddings. Run /knowledge-embed.\n'
        stream = self.engine.stream_response(messages, temperature=RAG_TEMPERATURE)
        nonempty = False
        try:
            for chunk in stream:
                nonempty = nonempty or bool(chunk.strip())
                yield safe_display(chunk)
        finally:
            stream.close()
        if not nonempty:
            yield 'No answer was generated.'
        yield '\n\nEvidence supplied to model (not verified citations):\n'
        for source in sources:
            yield f"[{source['source']}] {safe_display(source['filename'])} | {safe_display(source['location'])}\n"
        yield 'AI-generated answer; verify against the original documents.'
