from core.rag_assistant import RAGEnabledKlubAI
from language.language_router import LanguageRouter


class LanguageEnabledKlubAI(RAGEnabledKlubAI):
    def __init__(self):
        super().__init__()
        self.language_router = LanguageRouter()
        self.last_language = None

    def chat_stream(self, user_message):
        response = self.language_router.route(user_message)
        if response is not None:
            yield response
            return
        # Detection is observational. Preserve existing routing and input.
        try:
            self.last_language = self.language_router.detector.detect(user_message)
        except ValueError:
            self.last_language = None
        yield from super().chat_stream(user_message)
