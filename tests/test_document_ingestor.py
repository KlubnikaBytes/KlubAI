import pytest
from knowledge.knowledge_database import KnowledgeDatabase
from knowledge.knowledge_manager import KnowledgeManager
from knowledge.knowledge_router import KnowledgeRouter

@pytest.fixture
def manager(tmp_path):
    return KnowledgeManager(KnowledgeDatabase(tmp_path/'test.db'), tmp_path/'docs')

def write(manager, name, text):
    (manager.ingestor.reader.validator.base_directory/name).write_text(text, encoding='utf-8')

def test_import(manager):
    write(manager,'a.txt','Billnika GST invoice')
    assert manager.ingest('a.txt')['chunks'] == 1
    assert manager.search('GST')[0]['filename'] == 'a.txt'

def test_duplicate(manager):
    write(manager,'a.txt','same content')
    write(manager,'b.txt','same content')
    manager.ingest('a.txt')
    with pytest.raises(ValueError): manager.ingest('b.txt')

def test_truncated(manager):
    write(manager,'a.txt','x'*30001)
    with pytest.raises(ValueError, match='extraction limits'): manager.ingest('a.txt')
    assert manager.statistics()['documents'] == 0

def test_empty(manager):
    write(manager,'a.txt','   ')
    with pytest.raises(ValueError): manager.ingest('a.txt')

def test_traversal(manager):
    with pytest.raises(ValueError): manager.ingest('../a.txt')

def test_bulk(manager):
    write(manager,'a.txt','valid knowledge')
    write(manager,'b.txt',' ')
    results = manager.ingest_all()
    assert len(results) == 2
    assert sum('error' in r for r in results) == 1

def test_router(manager):
    write(manager,'my file.txt','local knowledge')
    router = KnowledgeRouter(manager)
    assert 'my file.txt' in router.route('/knowledge-files')
    assert 'Imported:' in router.route('/knowledge-add "my file.txt"')
    assert 'Not imported:' in router.route('/knowledge-add-all')
    assert 'Usage:' in router.route('/knowledge-add')
