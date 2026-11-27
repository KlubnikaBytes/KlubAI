from config import RAG_MAX_CHUNKS, RAG_KNOWLEDGE_TOKENS, RAG_TEMPERATURE

class RAGRouter:
    def __init__(self, engine):
        self.engine = engine
        self.enabled = False

    def route(self, message):
        parts = message.strip().split(maxsplit=1)
        if not parts:
            return None
        command = parts[0].lower()
        arg = parts[1].strip() if len(parts) == 2 else ''
        if command == '/ask-knowledge':
            return self.engine.answer(arg) if arg else iter(['Usage: /ask-knowledge question'])
        if command == '/rag-help' and not arg:
            return iter(['/ask-knowledge question\n/rag-info\n/rag-on\n/rag-off\nAutomatic mode handles questions beginning with About Billnika or About KlubAI.'])
        if command == '/rag-info' and not arg:
            return iter([f'Automatic RAG: {self.enabled}\nMaximum chunks: {RAG_MAX_CHUNKS}\nEvidence token budget: {RAG_KNOWLEDGE_TOKENS}\nTemperature: {RAG_TEMPERATURE}\nAnswer mode: validated excerpts + local section selection'])
        if command in ('/rag-on', '/rag-off') and not arg:
            self.enabled = command == '/rag-on'
            return iter([f'Automatic RAG: {self.enabled} (current process only)'])
        if command.startswith('/rag-'):
            return iter(['Unknown or incomplete RAG command. Use /rag-help.'])
        if self.enabled and message.strip().lower().startswith(('about billnika ', 'about klubai ')):
            return self.engine.answer(message.strip())
        return None
