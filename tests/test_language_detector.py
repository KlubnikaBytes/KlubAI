import pytest
from language.language_detector import LanguageDetector

@pytest.mark.parametrize('text,code', [
    ('What is Python?', 'en'), ('पाइथन क्या है?', 'hi'),
    ('পাইথন কী?', 'bn'), ('Python kya hai?', 'hinglish'),
    ('Python में function कैसे बनाएं?', 'mixed-hi'),
    ('Python কীভাবে কাজ করে?', 'mixed-bn'), ('25 × 16', 'neutral'),
    ('/knowledge-status', 'command'), ('sample.pdf', 'neutral'),
    ('print("hello")', 'neutral'), ('你好', 'unknown'),
    ('नमस्ते বাংলা', 'mixed'), ('', 'neutral'), ('😀', 'neutral'),
    ('KlubAI', 'unknown'), ('D:\\KlubAI', 'neutral'),
    ('https://example.com', 'neutral'), ('/read বাংলা.pdf', 'command'),
])
def test_detection(text, code):
    assert LanguageDetector().detect(text).code == code

def test_length():
    with pytest.raises(ValueError):
        LanguageDetector().detect('a' * 10001)

def test_type():
    with pytest.raises(TypeError):
        LanguageDetector().detect(None)
