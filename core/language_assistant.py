from core.rag_assistant import RAGEnabledKlubAI
from language.language_router import LanguageRouter
from language.language_preferences import LanguagePreferences
from language.language_selector import LanguageSelector
from language.language_prompt import apply_language, reinforce_language
from language.response_validator import matches_language
from language.context_isolation import isolate_context


class LanguageEnabledKlubAI(RAGEnabledKlubAI):
    def __init__(self):
        super().__init__()
        self.preferences = LanguagePreferences(self.conversation.database)
        self.language_router = LanguageRouter(preferences=self.preferences)
        self.selector = LanguageSelector()
        self.last_language = None

    def get_conversation_messages(self):
        messages = super().get_conversation_messages()
        text = messages[-1]["content"]
        try:
            code = self.language_router.detector.detect(text).code
        except ValueError:
            code = "unknown"
        self.response_language = self.selector.select(self.preferences.get(), code)
        return apply_language(isolate_context(messages, self.response_language), self.response_language)

    def stream_chat_response(self, messages):
        code = self.response_language
        for retry in (False, True):
            stream = self.engine.stream_response(reinforce_language(messages, code, retry), temperature=0.2)
            try:
                answer = "".join(stream).strip()
            finally:
                stream.close()
            if matches_language(answer, code):
                yield answer
                return
        raise RuntimeError("Unable to generate a response in the selected language. Try rephrasing or /language en.")

    def clear_conversation(self):
        super().clear_conversation()
        self.selector.reset()
        self.last_language = None

    def chat_stream(self, user_message):
        response = self.language_router.route(user_message)
        if response is not None:
            if user_message.strip().lower() in ("/language-reset", "/language auto"):
                self.selector.reset()
            yield response
            return
        try:
            self.last_language = self.language_router.detector.detect(user_message)
        except ValueError:
            self.last_language = None
        yield from super().chat_stream(user_message)
        if user_message.strip().lower() == "/delete-data confirm":
            self.selector.reset()
            self.last_language = None
