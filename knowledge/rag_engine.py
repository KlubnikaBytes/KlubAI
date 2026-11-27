import json
from knowledge.evidence_selector import select_evidence
from knowledge.answer_recovery import validate_recovered
from config import RAG_MAX_CHUNKS, RAG_TEMPERATURE
from knowledge.context_builder import ContextBuilder
from knowledge.vector_search import validate_query
from knowledge.knowledge_router import safe_display
from knowledge.evidence_filter import filter_evidence
from knowledge.answer_validator import validate_answer, NO_ANSWER
from knowledge.citation_manager import render_sources

class RAGEngine:
    def __init__(self, engine, manager):
        self.engine = engine
        self.manager = manager
        self.builder = ContextBuilder(engine)

    def answer(self, question):
        try:
            validate_query(question, RAG_MAX_CHUNKS)
        except ValueError:
            yield 'Enter a searchable question of up to 1000 characters.'
            return
        if not self.engine.is_loaded():
            raise RuntimeError('Local model is not loaded.')
        rows = filter_evidence(question, self.manager.hybrid_search(question, limit=30))
        messages, sources = self.builder.build(question, rows)
        if not sources:
            yield NO_ANSWER
            return
        pending = self.manager.embedding_store().statistics()['pending']
        if pending:
            yield f'Warning: {pending} chunks lack embeddings. Run /knowledge-embed.\n'
        selections = select_evidence(question, sources)
        if selections is not None:
            answer, ids = validate_answer(json.dumps(selections), sources)
        else:
            stream = self.engine.stream_response(messages, temperature=RAG_TEMPERATURE)
            try:
                raw = ''.join(stream)
            finally:
                stream.close()
            try:
                answer, ids = validate_recovered(raw, sources)
            except ValueError:
                yield NO_ANSWER
                return
        yield safe_display(answer)
        if ids:
            yield '\n\nSources (exact excerpts checked):\n' + render_sources(ids, sources)
            yield '\nExcerpt relevance and completeness are not guaranteed.'
