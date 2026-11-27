"""Non-executable Hindi analysis views; preserve original user input."""
import unicodedata as ud
from dataclasses import dataclass

@dataclass(frozen=True)
class HindiText:
    normalized: str
    devanagari_letters: int
    latin_letters: int
    devanagari_digits: int


def analyze_hindi(text: str) -> HindiText:
    if not isinstance(text, str):
        raise TypeError('Text must be a string.')
    if len(text) > 10000:
        raise ValueError('Hindi analysis input exceeds 10000 characters.')
    normalized = ud.normalize('NFC', text)
    # Preserve vowel signs, nukta, virama and joiners. Only fold whitespace.
    normalized = ' '.join(normalized.split())
    names = [ud.name(c, '') for c in normalized if c.isalpha()]
    return HindiText(normalized,
                     sum(n.startswith('DEVANAGARI ') for n in names),
                     sum(n.startswith('LATIN ') for n in names),
                     sum('\u0966' <= c <= '\u096f' for c in normalized))


def hindi_search_key(text: str) -> str:
    """Comparison only: fold Devanagari digits and Latin case, not spelling."""
    return analyze_hindi(text).normalized.translate(
        str.maketrans('०१२३४५६७८९', '0123456789')).casefold()


def safe_preview(text: str) -> str:
    return ''.join(c if not ud.category(c).startswith('C') or c in '\u200c\u200d'
                   else f'\\u{ord(c):04x}' for c in text)
