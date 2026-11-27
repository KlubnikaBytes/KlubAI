import re
import unicodedata
from dataclasses import dataclass
from language.language_registry import LANGUAGES
from language.text_normalizer import normalize_text


@dataclass(frozen=True)
class Detection:
    code: str
    confidence: str
    reason: str

    @property
    def name(self):
        return LANGUAGES[self.code]


class LanguageDetector:
    MAX_LENGTH = 10000
    ROMAN_HINDI = frozenset('kya hai hain kaise kaun kahan kyun nahi nahin mujhe mera meri aap tum batao karo karein chahiye kaam hindi mein samjhao ek iska iske iski hota hoti hote karta karti karte karna liye aur bahut agar lekin wala wali sakta sakti sakte jawab istemal zaroori'.split())
    ENGLISH = frozenset('what is are how who where why when the a an this that can you please explain create write hello hi thanks good tell me about python invoice function report'.split())

    def detect(self, text):
        if not isinstance(text, str):
            raise TypeError('Text must be a string.')
        if len(text) > self.MAX_LENGTH:
            raise ValueError('Detection input exceeds 10000 characters.')
        text = normalize_text(text)
        def result(code, confidence, reason):
            return Detection(code, confidence, reason)
        if re.match(r'^/[A-Za-z][\w-]*(?:\s|$)', text):
            return result('command', 'high', 'Slash command syntax')
        if (re.fullmatch(r'[^\s/\\]+\.(?:pdf|docx|xlsx|csv|txt|md|json|pptx|py|js|php|dart|exe)', text, re.I)
                or re.match(r'^(?:[A-Za-z]:[\\/]|\\\\|https?://)', text)
                or text.startswith('```')
                or re.match(r'^(?:def |class |import |from \w+ import |print\(|SELECT\s)', text)):
            return result('neutral', 'high', 'File, path, URL or recognizable code')
        scripts = set()
        for char in text:
            if not char.isalpha():
                continue
            name = unicodedata.name(char, '')
            scripts.add('hi' if name.startswith('DEVANAGARI ') else 'bn' if name.startswith('BENGALI ') else 'latin' if name.startswith('LATIN ') else 'other')
        if not scripts:
            return result('neutral', 'high', 'No alphabetic characters')
        if scripts == {'hi'}:
            return result('hi', 'medium', 'Devanagari script; language inferred')
        if scripts == {'bn'}:
            return result('bn', 'medium', 'Bengali script; language inferred')
        if scripts == {'hi', 'latin'}:
            return result('mixed-hi', 'medium', 'Devanagari and Latin scripts')
        if scripts == {'bn', 'latin'}:
            return result('mixed-bn', 'medium', 'Bengali and Latin scripts')
        if len(scripts) > 1:
            return result('mixed', 'medium', 'Multiple alphabetic scripts')
        if scripts != {'latin'}:
            return result('unknown', 'low', 'Unsupported script')
        words = set(re.findall(r'[a-z]+', text.casefold()))
        if len(words & self.ROMAN_HINDI) >= 2:
            return result('hinglish', 'medium', 'Romanized Hindi word matches')
        if words & self.ENGLISH:
            return result('en', 'medium', 'English word matches')
        return result('unknown', 'low', 'Latin text without sufficient language evidence')
