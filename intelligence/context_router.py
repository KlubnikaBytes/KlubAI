from intelligence.context_relevance import ContextRelevance
from language.context_isolation import isolate_context
from language.language_selector import LanguageSelector

CONTEXT_COMMANDS = {
    '/context-info': 'Show context filtering status',
    '/context-help': 'Show context commands',
    '/context-preview question': 'Inspect context selection without inference',
    '/context-on': 'Enable context filtering for this run',
    '/context-off': 'Disable context filtering for this run',
}

class ContextRouter:
    def __init__(self, assistant):
        self.assistant = assistant
        self.engine = ContextRelevance()
        self.enabled = True

    def route(self, message):
        parts = message.strip().split(maxsplit=1)
        if not parts:
            return None
        cmd = parts[0].lower()
        if cmd == '/context-preview' and len(parts)==2:
            question = parts[1]
            if len(question)>10000:
                return 'Preview question exceeds 10000 characters.'
            a = self.assistant
            selector = LanguageSelector()
            selector.last = a.selector.last
            code = selector.select(a.preferences.get(), a.language_router.detector.detect(question).code)
            messages = [*a.conversation.get_messages(), {'role':'user','content':question}]
            compatible = isolate_context(messages, code)
            result = self.engine.select(compatible, self.enabled and code == 'en')
            lines = [f'Language: {code}', f'Compatible turns: {(len(compatible)-2)//2}', f'Selected turns: {(len(result.messages)-2)//2}', result.reason]
            lines.extend(f'Turn {i}: score={score:.3f}; {"keep" if keep else "exclude"}' for i,score,keep in result.scores)
            return '\n'.join(lines)
        if len(parts)==1:
            if cmd == '/context-help':
                return '\n'.join(f'{k}: {v}' for k,v in CONTEXT_COMMANDS.items())
            if cmd == '/context-info':
                return f'Context relevance: {"enabled" if self.enabled else "disabled"}\nScope: English general chat; session-only setting; history unchanged.'
            if cmd in ('/context-on','/context-off'):
                self.enabled = cmd == '/context-on'
                return f'Context relevance: {"enabled" if self.enabled else "disabled"}'
        if cmd.startswith('/context-'):
            return 'Invalid context command. Use /context-help.'
        return None
