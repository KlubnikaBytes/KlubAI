from language.hindi_normalizer import analyze_hindi, hindi_search_key, safe_preview
from language.language_detector import LanguageDetector
from language.language_registry import LANGUAGES

LANGUAGE_COMMANDS = {
    "/hindi-help": "Show Hindi text analysis commands",
    "/hindi-normalize text": "Preview normalized Hindi text",
    "/hindi-analyze text": "Inspect Hindi script and search key",
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
        if command.startswith('/hindi-'):
            if command == '/hindi-help' and not arg:
                return '\n'.join(f'{k} - {v}' for k, v in LANGUAGE_COMMANDS.items() if k.startswith('/hindi-'))
            if command not in ('/hindi-normalize', '/hindi-analyze') or not arg:
                return 'Use /hindi-help.'
            try:
                result = analyze_hindi(arg)
            except ValueError as error:
                return str(error)
            preview = safe_preview(result.normalized)
            if command == '/hindi-normalize':
                return 'Normalized preview: ' + preview
            return (f'Normalized preview: {preview}\n'
                    f'Search key: {safe_preview(hindi_search_key(arg))}\n'
                    f'Devanagari letters: {result.devanagari_letters}\n'
                    f'Latin letters: {result.latin_letters}\n'
                    f'Devanagari digits: {result.devanagari_digits}\n'
                    'Analysis only; no commands executed.')
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
