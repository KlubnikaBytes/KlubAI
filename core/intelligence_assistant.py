from core.language_assistant import LanguageEnabledKlubAI
from intelligence.intelligence_router import IntelligenceRouter


class IntelligenceEnabledKlubAI(LanguageEnabledKlubAI):
    def __init__(self):
        super().__init__()
        self.intelligence_router = IntelligenceRouter()
        self.last_intent = None

    def chat_stream(self, user_message):
        response = self.intelligence_router.route(user_message)
        if response is not None:
            yield response
            return
        try:
            self.last_intent = self.intelligence_router.classifier.classify(user_message)
        except ValueError:
            self.last_intent = None
        yield from super().chat_stream(user_message)

    def clear_conversation(self):
        super().clear_conversation()
        self.last_intent = None
