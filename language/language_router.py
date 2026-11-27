from language.language_detector import LanguageDetector
from language.language_registry import LANGUAGES

LANGUAGE_COMMANDS = {
    '/language [auto|en|hi|bn|hinglish]': 'Show or set response preference',
    '/language-reset': 'Reset response preference',
    '/language-help': 'Show language detection commands',
    '/languages': 'List detection categories',
    '/language-info': 'Show language detection configuration',
    '/detect-language text': 'Detect language of supplied text',
}


class LanguageRouter:
    def __init__(self, detector=None, preferences=None):
        self.preferences = preferences
        self.detector = detector or LanguageDetector()

    def route(self, message):
        parts = message.strip().split(maxsplit=1)
        if not parts:
            return None
        command = parts[0].lower()
        arg = parts[1] if len(parts) == 2 else ''
        if command in ('/language', '/language-reset'):
            if self.preferences is None:
                return 'Language preferences unavailable.'
            if command == '/language-reset':
                if arg:
                    return 'Usage: /language-reset'
                self.preferences.reset()
                return 'Language preference reset: auto'
            if not arg:
                return 'Language preference: ' + self.preferences.get()
            try:
                self.preferences.set(arg.lower())
            except ValueError as error:
                return str(error)
            return 'Language preference saved: ' + self.preferences.get()
        if command == '/detect-language':
            if not arg:
                return 'Usage: /detect-language text'
            try:
                detected = self.detector.detect(arg)
            except ValueError as error:
                return str(error)
            return f'Language: {detected.name}\nCode: {detected.code}\nConfidence: {detected.confidence} (heuristic)\nReason: {detected.reason}'
        if command == '/languages' and not arg:
            return '\n'.join(f'{code}: {name}' for code, name in LANGUAGES.items())
        if command == '/language-help' and not arg:
            return '\n'.join(f'{cmd} - {desc}' for cmd, desc in LANGUAGE_COMMANDS.items())
        if command == '/language-info' and not arg:
            return 'Engine: local Unicode and word rules\nExternal API: not required\nAutomatic detection: enabled\nResponse language switching: enabled for general AI chat (all generated chat responses buffered and checked; one retry)\nPreference: ' + (self.preferences.get() if self.preferences else 'unavailable') + '\nConfidence: qualitative, not calibrated'
        if command.startswith('/language-') or command == '/languages':
            return 'Unknown or incomplete language command. Use /language-help.'
        return None
