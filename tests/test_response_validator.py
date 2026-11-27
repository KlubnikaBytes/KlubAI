import pytest
from language.response_validator import matches_language
from language.language_prompt import reinforce_language

@pytest.mark.parametrize('text,code,expected', [
 ('Python is a programming language.', 'hi', False),
 ('Python is a programming language.', 'bn', False),
 ('Python is a programming language.', 'hinglish', False),
 ('पाइथन एक प्रोग्रामिंग भाषा है।', 'hi', True),
 ('পাইথন একটি প্রোগ্রামিং ভাষা।', 'bn', True),
 ('Python ek programming language hai. Isse kaam karo.', 'hinglish', True),
 ('পাইথন একটি ভাষা।', 'hi', False),
 ('```python\nprint(1)\n```', 'hi', True),
 ('400', 'bn', True),
 ('', 'hi', False),
])
def test_language(text, code, expected):
    assert matches_language(text, code) == expected

def test_reinforcement():
    messages = [{'role':'system','content':'base'}, {'role':'user','content':'old'}, {'role':'assistant','content':'old answer'}, {'role':'user','content':'question'}]
    result = reinforce_language(messages, 'hi', True)
    assert len(result) == 2
    assert 'Devanagari' in result[-1]['content']
    assert messages[-1]['content'] == 'question'
