from language.text_normalizer import normalize_text

def test_nfc():
    assert normalize_text(' e\u0301 ') == 'é'

def test_preserve_scripts():
    assert normalize_text('বাংলা हिंदी') == 'বাংলা हिंदी'

def test_preserve_internal_whitespace():
    assert normalize_text('a  b\nc') == 'a  b\nc'
