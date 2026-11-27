import json
from intelligence.benchmark_router import BenchmarkRouter
from intelligence.benchmark_engine import BenchmarkEngine

class FakeModel:
    model_id = 'fake'
    def stream_response(self, messages, temperature):
        yield 'An English answer.'

def test_components():
    rows = BenchmarkEngine(FakeModel()).run('components')['rows']
    assert len(rows)==23
    assert all(r['status']=='pass' for r in rows), rows

def test_model_manual():
    rows = BenchmarkEngine(FakeModel()).run('model')['rows']
    assert len(rows)==6
    assert all(r['status']=='manual_review' for r in rows)

def test_router(tmp_path):
    r = BenchmarkRouter(FakeModel(),tmp_path)
    assert r.route('Hello') is None
    assert 'No benchmark' in r.route('/benchmark-results')
    assert 'pass: 23' in r.route('/benchmark-run components')
    assert 'twice' in r.route('/benchmark-compare')
    r.route('/benchmark-run components')
    assert 'Previous:' in r.route('/benchmark-compare')
    assert 'exported' in r.route('/benchmark-export')
    assert len(json.loads(next(tmp_path.glob('*.json')).read_text())['rows'])==23
    assert r.route('/benchmark-run /delete-data confirm')=='See /benchmark-help.'
