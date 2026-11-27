from intelligence.verification_router import VerificationRouter
from intelligence.fact_router import FactRouter
from intelligence.quality_router import QualityRouter
from intelligence.context_router import ContextRouter
from core.language_assistant import LanguageEnabledKlubAI
from intelligence.intelligence_router import IntelligenceRouter


class IntelligenceEnabledKlubAI(LanguageEnabledKlubAI):
    def __init__(self):
        super().__init__()
        self.intelligence_router = IntelligenceRouter()
        self.last_intent = None
        self.context_router = ContextRouter(self)
        self.quality_router = QualityRouter()
        self.fact_router = FactRouter()
        self.verification_router = VerificationRouter(self.fact_router.engine.registry)

    def get_conversation_messages(self):
        messages = super().get_conversation_messages()
        return self.context_router.engine.select(messages, self.context_router.enabled and self.response_language == "en").messages

    def stream_chat_response(self, messages):
        # Parent already buffers and validates the selected language.
        stream = super().stream_chat_response(messages)
        try:
            answer = "".join(stream)
        finally:
            stream.close()
        if self.response_language == "en" and self.quality_router.enabled:
            try:
                self.quality_router.record(messages[-1]["content"], answer)
            except ValueError:
                pass  # Unsupported assessment input must not block chat.
        if self.response_language == "en" and self.verification_router.enabled:
            try:
                self.verification_router.record(answer)
            except ValueError:
                pass
        yield answer

    def handle_direct_question(self, message):
        response = super().handle_direct_question(message)
        if response is not None:
            return response
        if self.fact_router.enabled and self.preferences.get() in ("auto", "en"):
            return self.fact_router.engine.answer(message)
        return None

    def chat_stream(self, user_message):
        response = self.verification_router.route(user_message)
        if response is not None:
            yield response
            return
        response = self.fact_router.route(user_message)
        if response is not None:
            yield response
            return
        response = self.quality_router.route(user_message)
        if response is not None:
            yield response
            return
        response = self.context_router.route(user_message)
        if response is not None:
            yield response
            return
        response = self.intelligence_router.route(user_message)
        if response is not None:
            yield response
            return
        try:
            self.last_intent = self.intelligence_router.classifier.classify(user_message)
        except ValueError:
            self.last_intent = None
        yield from super().chat_stream(user_message)
        if user_message.strip().lower() == "/delete-data confirm":
            self.quality_router.reset()
            self.verification_router.reset()

    def clear_conversation(self):
        super().clear_conversation()
        self.quality_router.reset()
        self.verification_router.reset()
        self.last_intent = None
