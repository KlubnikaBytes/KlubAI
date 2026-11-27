import pytest
from intelligence.answer_verifier import AnswerVerifier
from intelligence.verification_router import VerificationRouter

@pytest.mark.parametrize('text,expected',[
    ('Python was created by Guido van Rossum.',(1,0,0)),
    ('Python was not created by Guido van Rossum.',(0,1,0)),
    ('Python was created by Taylor Otwell.',(0,0,1)),
    ('Laravel is a PHP web application framework.',(1,0,0)),
    ('Laravel is not a PHP web application framework.',(0,1,0)),
    ('Java is a language.',(0,0,1)),
    ('Python was created by Guido van Rossum. Java is a language.',(1,0,1)),
    ('Python was created by Guido van Rossum and aliens.',(0,0,1)),
    ('```Python was created by Guido van Rossum.```',(0,0,1)),
])
def test_claims(text,expected):
    r=AnswerVerifier().assess(text)
    assert (r.supported,r.contradicted,r.unverified)==expected

@pytest.mark.parametrize('text',['',' ',None,'x'*20001])
def test_invalid(text):
    with pytest.raises(ValueError): AnswerVerifier().assess(text)

def test_urls():
    r=AnswerVerifier().assess('https://docs.python.org/3/faq/general.html https://example.org')
    assert (r.known_urls,r.unknown_urls)==(1,1)

def test_router():
    r=VerificationRouter()
    assert r.route('/memory') is None
    assert 'No automatic' in r.route('/verify-last')
    assert 'Supported: 1' in r.route('/verify-answer Python was created by Guido van Rossum.')
    assert r.count==0
    r.record('Python was created by Guido van Rossum.')
    assert r.count==1 and r.supported==1
    r.route('/verify-off'); r.record('Unknown claim.')
    assert r.count==1
    r.route('/verify-on'); r.reset()
    assert r.count==0 and r.last is None
    assert 'Invalid' in r.route('/verify-answer')
