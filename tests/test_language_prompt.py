import pytest
from language.language_prompt import apply_language

@pytest.mark.parametrize("code,word", [("en","English"),("hi","Devanagari"),("bn","Bengali"),("hinglish","Latin")])
def test_prompt(code, word):
    messages = [{"role":"system","content":"Base"},{"role":"user","content":"Original"}]
    result = apply_language(messages, code)
    assert word in result[0]["content"]
    assert messages[0]["content"] == "Base"
    assert result[1] == messages[1]

def test_invalid_messages():
    with pytest.raises(ValueError):
        apply_language([], "en")
