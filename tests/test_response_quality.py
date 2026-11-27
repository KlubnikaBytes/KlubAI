import pytest
from intelligence.response_quality import ResponseQuality
from intelligence.quality_router import QualityRouter

@pytest.mark.parametrize('question,answer,issue',[
 ('What is Python?','Python is a general-purpose programming language.',None),
 ('What is Python?','GST is a consumption tax on goods.','overlap'),
 ('Explain Python','Python language','short'),
 ('Explain Python','Python is useful because','unfinished'),
 ('Write code','```python\nprint(1)','fence'),
 ('Explain Python','Python is a useful language. Python is a useful language.','Repeated'),
 ('What is Python?','Python '+ 'word '*351,'Long answer'),
 ('What is Python?','Python is useful. This is guaranteed correct.','certainty'),
 ('Explain Python','Python is useful\x1b.','control'),
 ('Explain Python','   ','Empty'),
])
def test_assessment(question,answer,issue):
    report=ResponseQuality().assess(question,answer)
    assert 0<=report.score<=100
    assert report.score==sum(report.components.values())
    if issue is None:
        assert report.score==100 and not report.issues
    else:
        assert any(issue in item for item in report.issues)

@pytest.mark.parametrize('q,a',[('', 'answer'),('x'*10001,'answer'),('question','x'*50001),(None,'answer')])
def test_limits(q,a):
    with pytest.raises(ValueError):
        ResponseQuality().assess(q,a)

def test_router():
    r=QualityRouter()
    assert r.route('hello') is None
    assert 'No automatic' in r.route('/quality-last')
    assert '100/100' in r.route('/quality-check What is Python? | Python is a programming language.')
    assert r.count==0
    r.record('What is Python?','Python is a programming language.')
    assert r.count==1 and r.total==100
    assert '100.00' in r.route('/quality-stats')
    r.route('/quality-off')
    r.record('What is Python?','wrong')
    assert r.count==1
    r.route('/quality-on')
    r.record('What is Python?','wrong')
    assert r.count==2 and r.flagged==1
    r.reset()
    assert r.count==0 and r.last is None
    assert 'Invalid' in r.route('/quality-check')
    assert 'nonempty' in r.route('/quality-check | answer')
    assert 'observation' in r.route('/quality-info')
