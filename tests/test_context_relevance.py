import pytest
from intelligence.context_relevance import ContextRelevance
from intelligence.context_router import ContextRouter

def msg(role,content): return dict(role=role,content=content)
def history(q):
    return [msg('system','system'),msg('user','What is Python?'),msg('assistant','Python is a programming language.'),msg('user','What is GST?'),msg('assistant','GST is a tax.'),msg('user',q)]

@pytest.mark.parametrize('q,count',[('What is MySQL?',0),('Who invented Python?',1),('Explain GST',1),('Explain it in more detail',2),('xyz',2),('Python क्या है?',2),('What is it?',2)])
def test_selection(q,count):
    original=history(q); snapshot=[dict(m) for m in original]
    result=ContextRelevance().select(original)
    assert len(result.messages)==2+2*count
    assert result.messages[0]==original[0] and result.messages[-1]==original[-1]
    assert original==snapshot

def test_disabled():
    h=history('What is MySQL?'); assert ContextRelevance().select(h,False).messages==h

def test_orphan():
    h=history('What is MySQL?'); del h[1]; assert len(ContextRelevance().select(h).messages)==2

def test_invalid():
    with pytest.raises(ValueError): ContextRelevance().select([])

def test_commands():
    r=ContextRouter(None)
    assert 'disabled' in r.route('/context-off')
    assert 'enabled' in r.route('/context-on')
    assert '/context-preview' in r.route('/context-help')
    assert r.route('hello') is None
    assert 'Invalid' in r.route('/context-off extra')
