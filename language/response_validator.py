import re
import unicodedata
from language.language_detector import LanguageDetector


def matches_language(text, code):
    if code not in ('en', 'hi', 'bn', 'hinglish') or not text.strip():
        return False
    prose = re.sub(r'```[\s\S]*?```|`[^`]*`|https?://\S+', '', text)
    letters = [c for c in prose if c.isalpha()]
    if not letters:
        return bool(text.strip())
    counts = {s: sum(unicodedata.name(c, '').startswith(s) for c in letters)
              for s in ('DEVANAGARI ', 'BENGALI ', 'LATIN ')}
    words = set(re.findall(r'[a-z]+', prose.lower()))
    markers = words & LanguageDetector.ROMAN_HINDI
    if code in ('hi', 'bn'):
        target = 'DEVANAGARI ' if code == 'hi' else 'BENGALI '
        other = 'BENGALI ' if code == 'hi' else 'DEVANAGARI '
        return counts[target] / len(letters) >= .35 and counts[other] == 0
    if counts['LATIN '] / len(letters) < .9:
        return False
    if code == 'hinglish':
        return len(markers) >= 2
    return len(markers) < 2
