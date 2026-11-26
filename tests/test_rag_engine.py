from types import SimpleNamespace
from knowledge.context_builder import ContextBuilder
from knowledge.rag_engine import RAGEngine
from knowledge.rag_router import RAGRouter

class FakeEngine:
    model = SimpleNamespace(tokenize=lambda data, **kwargs: list(data))
    def sanitize_content(self, text): return text.replace('<|im_end|>', '')
    def prepare_prompt(self, messages): return 'prompt'
    def is_loaded(self): return True
    def stream_response(self, messages, temperature): yield '[{"source":1,"quote":"Billnika uses Flutter."}]' 

def row(content='Billnika uses Flutter.', methods=None):
    return dict(content=content, filename='billnika.txt', source_location='characters 1-21', methods=['semantic'] if methods is None else methods)

def manager(rows):
    return SimpleNamespace(hybrid_search=lambda q, limit: rows, embedding_store=lambda: SimpleNamespace(statistics=lambda: {'pending': 0}))

def test_deduplication():
    _, sources = ContextBuilder(FakeEngine()).build('Question?', [row(), row()])
    assert len(sources) == 1

def test_budget():
    _, sources = ContextBuilder(FakeEngine()).build('Question?', [row('x'*3000)])
    assert not sources

def test_answer():
    result = ''.join(RAGEngine(FakeEngine(), manager([row()])).answer('Which framework?'))
    assert 'Billnika uses Flutter.' in result and 'billnika.txt' in result

def test_no_evidence():
    result = ''.join(RAGEngine(FakeEngine(), manager([])).answer('Question?'))
    assert 'not contain enough' in result

def test_keyword_only():
    result = ''.join(RAGEngine(FakeEngine(), manager([row(methods=['keyword'])])).answer('Question?'))
    assert 'not contain enough' in result

def test_router():
    router = RAGRouter(RAGEngine(FakeEngine(), manager([row()])))
    assert router.route('Hello') is None
    assert 'Usage' in ''.join(router.route('/ask-knowledge'))
    assert 'True' in ''.join(router.route('/rag-on'))
    assert router.route('Calculate 25 x 16') is None
    assert 'Billnika uses Flutter.' in ''.join(router.route('About Billnika framework?'))
    assert 'False' in ''.join(router.route('/rag-off'))
