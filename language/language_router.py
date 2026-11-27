from language.language_detector import LanguageDetector
from language.language_registry import LANGUAGES

LANGUAGE_COMMANDS = {
    '/language-help': 'Show language detection commands',
    '/languages': 'List detection categories',
    '/language-info': 'Show language detection configuration',
    '/detect-language text': 'Detect language of supplied text',
}


class LanguageRouter:
    def __init__(self, detector=None):
        self.detector = detector or LanguageDetector()

    def route(self, message):
        parts = message.strip().split(maxsplit=1)
        if not parts:
            return None
        command = parts[0].lower()
        arg = parts[1] if len(parts) == 2 else ''
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
            return 'Engine: local Unicode and word rules\nExternal API: not required\nAutomatic detection: enabled\nResponse language switching: not implemented yet\nConfidence: qualitative, not calibrated'
        if command.startswith('/language-') or command == '/languages':
            return 'Unknown or incomplete language command. Use /language-help.'
        return None
