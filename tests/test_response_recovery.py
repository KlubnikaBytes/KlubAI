import pytest
from types import SimpleNamespace
from intelligence.response_recovery import ResponseRecovery
from intelligence.response_quality import ResponseQuality
from intelligence.answer_verifier import AnswerVerifier
from intelligence.factual_knowledge import FactualKnowledge
from intelligence.recovery_router import RecoveryRouter

@pytest.fixture
def engine():
    facts = FactualKnowledge()
    return ResponseRecovery(ResponseQuality(), AnswerVerifier(facts.registry), facts)

@pytest.mark.parametrize('answer', ['Python is a general-purpose programming language.', 'Python was created by Taylor Otwell.', 'Python supports many applications.'])
def test_unchanged(engine, answer):
    assert engine.recover('What is Python?', answer, lambda _: pytest.fail('unexpected retry')).outcome == 'unchanged'

@pytest.mark.parametrize('answer', ['Python is useful because', 'Python is useful for programming. Python is useful for programming.', '```python\nprint(1)', 'Python is useful\x1b', ''])
def test_retry(engine, answer):
    calls = []
    def retry(reasons):
        calls.append(reasons)
        return 'Python is a general-purpose programming language.'
    assert engine.recover('What is Python?', answer, retry).outcome == 'regenerated'
    assert len(calls)==1

def test_curated(engine):
    result = engine.recover('Who invented Python?', 'Python was not created by Guido van Rossum.', lambda _: pytest.fail('unexpected retry'))
    assert result.outcome == 'curated' and 'Fact ID: python_creator' in result.answer

@pytest.mark.parametrize('candidate', ['Python is useful because', 'বাংলা ভাষা', ''])
def test_fallback(engine, candidate):
    assert engine.recover('What is Python?', 'Python is useful because', lambda _: candidate).outcome == 'fallback'

def test_unknown_contradiction_scope(engine):
    assert engine.recover('Explain programming.', 'Python was not created by Guido van Rossum.', lambda _: 'Python is useful.').outcome == 'fallback'

def test_disabled_quality(engine):
    assert engine.recover('What is Python?', 'Python is useful because', lambda _: pytest.fail(), quality=False).outcome == 'unchanged'

def test_disabled_verification(engine):
    assert engine.recover('Who invented Python?', 'Python was not created by Guido van Rossum.', lambda _: pytest.fail(), verification=False).outcome == 'unchanged'

def test_router(engine):
    a = SimpleNamespace(quality_router=SimpleNamespace(engine=engine.quality,enabled=True), verification_router=SimpleNamespace(engine=engine.verifier,enabled=True),fact_router=SimpleNamespace(engine=engine.facts,enabled=True))
    r = RecoveryRouter(a)
    assert 'unfinished' in r.route('/recovery-preview What is Python? | Python is useful because')
    assert 'Preview only' in r.route('/recovery-preview /delete-data confirm | example')
    assert sum(r.counts.values()) == 0
    assert 'disabled' in r.route('/recovery-off')
    r.record(engine.recover('What is Python?', 'Python is useful.', lambda _: pytest.fail()))
    assert 'Unchanged: 1' in r.route('/recovery-stats')
    r.reset()
    assert 'No recovery' in r.route('/recovery-last')
