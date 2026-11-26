from core.analysis_assistant import AnalysisEnabledKlubAI
from knowledge.knowledge_router import KnowledgeRouter


class KnowledgeEnabledKlubAI(AnalysisEnabledKlubAI):
    def __init__(self):
        super().__init__()
        self.knowledge_router = KnowledgeRouter()

    def chat_stream(self, user_message):
        try:
            response = self.knowledge_router.route(user_message)
        except Exception as error:
            yield f'Knowledge error: {type(error).__name__}'
            return
        if response is not None:
            yield response
            return
        yield from super().chat_stream(user_message)
