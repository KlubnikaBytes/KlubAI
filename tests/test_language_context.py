from language.context_isolation import isolate_context
from language.response_validator import matches_language
from language.language_prompt import apply_language, reinforce_language
import pytest

@pytest.mark.parametrize('text,code,expected', [
 ('Laravel is a PHP framework.', 'en', True),
 ('লারাভেল একটি ফ্রেমওয়ার্ক।', 'en', False),
 ('Python ek language hai.', 'en', False),
 ('Python ek language hai.', 'hinglish', True),
 ('Iska istemal development ke liye hota hai.', 'hinglish', True),
 ('Python is a useful tool.', 'hinglish', False),
 ('हिंदी বাংলা', 'hi', False),
])
def test_validator(text,code,expected):
    assert matches_language(text,code) == expected

def test_isolation():
    messages = [dict(role=r,content=c) for r,c in [('system','base'),('assistant','orphan'),('user','old'),('assistant','বাংলা ভাষা'),('user','English question'),('assistant','English answer'),('user','latest')]]
    result = isolate_context(messages,'en')
    assert [m['content'] for m in result] == ['base','English question','English answer','latest']
    prompt = reinforce_language(apply_language(result,'en'),'en',True)
    assert len(prompt)==2
    assert messages[-1]['content']=='latest'
    assert len(messages)==7
