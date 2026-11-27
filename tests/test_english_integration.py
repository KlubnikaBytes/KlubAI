"""Exercise actual assistant routing with isolated databases and scripted inference."""
import pytest
from core import conversation, intelligence_assistant
from knowledge import knowledge_manager
from memory.database import Database
from knowledge.knowledge_database import KnowledgeDatabase
from tools import file_reader, file_generator

@pytest.fixture
def assistant(tmp_path, monkeypatch):
    monkeypatch.setattr(conversation, 'Database', lambda: Database(tmp_path / 'memory.db'))
    monkeypatch.setattr(knowledge_manager, 'KnowledgeDatabase', lambda: KnowledgeDatabase(tmp_path / 'knowledge.db'))
    monkeypatch.setattr(knowledge_manager.KnowledgeManager.__init__, '__defaults__', (None, tmp_path / 'documents'))
    monkeypatch.setattr(file_reader, 'BASE_DIR', tmp_path)
    monkeypatch.setattr(file_generator.FileGenerator.__init__, '__defaults__', (tmp_path / 'outputs',))
    a = intelligence_assistant.IntelligenceEnabledKlubAI()
    a.benchmark_router.output_dir = tmp_path / 'outputs'
    a.chat('/language en')
    def unexpected(*args, **kwargs):
        raise AssertionError('Unexpected model inference')
    monkeypatch.setattr(a.engine, 'stream_response', unexpected)
    yield a
    a.shutdown()

def script(a, monkeypatch, *answers):
    calls = []
    pending = iter(answers)
    def stream(messages, **kwargs):
        calls.append(messages)
        yield next(pending)
    monkeypatch.setattr(a.engine, 'stream_response', stream)
    return calls

@pytest.mark.parametrize('question,expected', [('Hello','Hello!'), ('Who invented Python?','Guido van Rossum'), ('Who created Laravel?','Taylor Otwell'), ('Calculate 25 x 16','400'), ('/gst 25000 18','29,500')])
def test_direct_routes(assistant, question, expected):
    assert expected in assistant.chat(question)
    assert assistant.quality_router.count == 0

def test_memory_and_diagnostic_isolation(assistant):
    assistant.chat('My favourite colour is green')
    before = assistant.get_history()
    assistant.chat('/classify /delete-data confirm')
    assistant.chat('/benchmark-run /delete-data confirm')
    assert assistant.get_history() == before
    assert assistant.chat('/recall favourite_colour') == 'green'

def test_general_model(assistant, monkeypatch):
    calls = script(assistant, monkeypatch, 'A compiler translates source code into another form.')
    answer = assistant.chat('Explain how a compiler works.')
    assert len(calls) == 1
    assert assistant.get_history()[-1]['content'] == answer
    assert assistant.quality_router.count == assistant.verification_router.count == 1

def test_recovery_final_history(assistant, monkeypatch):
    calls = script(assistant, monkeypatch, 'Python is useful because', 'Python is a general-purpose programming language.')
    assistant.chat('/fact-off')
    answer = assistant.chat('What is Python?')
    assert len(calls) == 2
    assert assistant.recovery_router.last[0] == 'regenerated'
    assert assistant.get_history()[-1]['content'] == answer
    assert assistant.verification_router.last.supported == 1

def test_fact_off_contradiction(assistant, monkeypatch):
    script(assistant, monkeypatch, 'Python was not created by Guido van Rossum.', 'Python was created by Guido van Rossum.')
    assistant.chat('/fact-off')
    assert 'could not produce' in assistant.chat('Who invented Python?')
    assert assistant.recovery_router.last[0] == 'fallback'

def test_disabled_metrics(assistant, monkeypatch):
    script(assistant, monkeypatch, 'Python is a general-purpose programming language.')
    for command in ('/fact-off','/quality-off','/verify-off','/recovery-off'):
        assistant.chat(command)
    assistant.chat('What is Python?')
    assert assistant.quality_router.count == assistant.verification_router.count == 0
    assert assistant.recovery_router.last is None

def test_new_preserves_memory(assistant, monkeypatch):
    assistant.chat('/remember project=KlubAI')
    script(assistant, monkeypatch, 'A compiler translates source code into another form.')
    assistant.chat('Explain how a compiler works.')
    assistant.clear_conversation()
    assert assistant.get_history() == []
    assert assistant.quality_router.count == assistant.verification_router.count == 0
    assert assistant.recovery_router.last is None
    assert assistant.chat('/recall project') == 'KlubAI'

def test_interrupted_model(assistant, monkeypatch):
    def interrupted(*args, **kwargs):
        raise KeyboardInterrupt
        yield ''
    monkeypatch.setattr(assistant.engine, 'stream_response', interrupted)
    with pytest.raises(KeyboardInterrupt):
        assistant.chat('Explain how a compiler works.')
    assert assistant.get_history() == []
    assert assistant.conversation.history == []


def test_private_read_whitespace(assistant, tmp_path):
    path = tmp_path / 'inputs' / 'private.txt'
    path.write_text('private integration test content', encoding='utf8')
    before = assistant.get_history()
    assert 'private integration test content' in assistant.chat('read\tprivate.txt')
    assert assistant.get_history() == before
