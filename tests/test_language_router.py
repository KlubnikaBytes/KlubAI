from language.language_router import LanguageRouter

def test_detect():
    assert 'Code: hi' in LanguageRouter().route('/detect-language नमस्ते')

def test_missing():
    assert 'Usage:' in LanguageRouter().route('/detect-language')

def test_passthrough():
    router = LanguageRouter()
    for text in ('/read sample.pdf', '/ask-knowledge What is Billnika?', 'Hello', '/calculate 25*16'):
        assert router.route(text) is None

def test_help():
    assert '/detect-language' in LanguageRouter().route('/language-help')

def test_languages():
    assert 'hinglish' in LanguageRouter().route('/languages')

def test_info():
    assert 'enabled for general AI chat' in LanguageRouter().route('/language-info')

def test_unknown():
    assert 'Unknown' in LanguageRouter().route('/language-invalid')
