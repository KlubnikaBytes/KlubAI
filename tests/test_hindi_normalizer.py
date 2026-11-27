import unicodedata
import pytest
from language.hindi_normalizer import analyze_hindi, hindi_search_key, safe_preview
from language.language_router import LanguageRouter

@pytest.mark.parametrize('text,expected', [('  नमस्ते   दुनिया  ','नमस्ते दुनिया'),('Python\tक्या है?','Python क्या है?'),('क़','क़'),('क्\u200dष','क्\u200dष'),('१२३।','१२३।'),('বাংলা','বাংলা'),('','')])
def test_normalize(text,expected):
    assert analyze_hindi(text).normalized == unicodedata.normalize('NFC',expected)

@pytest.mark.parametrize('text,expected',[('१२३','123'),('Python क्या है?','python क्या है?'),('१२.५०','12.50'),('क़','क़')])
def test_key(text,expected):
    assert hindi_search_key(text)==expected

def test_counts():
    r=analyze_hindi('क Python १२')
    assert (r.devanagari_letters,r.latin_letters,r.devanagari_digits)==(1,6,2)

def test_limit():
    with pytest.raises(ValueError): analyze_hindi('क'*10001)

def test_type():
    with pytest.raises(TypeError): analyze_hindi(None)

def test_preview():
    assert safe_preview('\x1b[31m') == r'\u001b[31m'

def test_router():
    r=LanguageRouter()
    assert '123' in r.route('/hindi-analyze १२३')
    assert '/hindi-normalize' in r.route('/hindi-help')
    assert '/delete-data confirm' in r.route('/hindi-normalize /delete-data confirm')
    assert r.route('/hindi-analyze') == 'Use /hindi-help.'
    assert r.route('Hello') is None
