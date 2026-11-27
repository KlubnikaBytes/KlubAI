from core.knowledge_assistant import KnowledgeEnabledKlubAI
from knowledge.rag_engine import RAGEngine
from knowledge.rag_router import RAGRouter

class RAGEnabledKlubAI(KnowledgeEnabledKlubAI):
    def __init__(self):
        super().__init__()
        self.rag_router = RAGRouter(RAGEngine(self.engine, self.knowledge_router.manager))

    def chat_stream(self, user_message):
        try:
            response = self.rag_router.route(user_message)
            if response is not None:
                yield from response
                return
        except Exception as error:
            yield f'RAG error: {type(error).__name__}. Check the query, local model and embeddings.'
            return
        yield from super().chat_stream(user_message)
