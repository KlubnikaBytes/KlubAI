import hashlib
import pytest
from knowledge.knowledge_database import KnowledgeDatabase
from knowledge.knowledge_manager import KnowledgeManager
from knowledge.knowledge_router import KnowledgeRouter

@pytest.fixture
def db(tmp_path):
    return KnowledgeDatabase(tmp_path / 'knowledge.db')

def add(db, name='sample.txt', text='KlubAI is developed by Klubnika Bytes.'):
    return db.add_document(name, hashlib.sha256(text.encode()).hexdigest(), 'TXT', len(text.encode()), [(text, 'Section 1')])

def test_empty(db):
    assert db.statistics() == {'documents':0,'chunks':0}

def test_add(db):
    assert add(db) > 0
    assert db.statistics() == {'documents':1,'chunks':1}

def test_list(db):
    add(db)
    assert db.list_documents()[0]['chunk_count'] == 1

def test_search(db):
    add(db)
    assert db.search('KlubAI')[0]['filename'] == 'sample.txt'

def test_case(db):
    add(db)
    assert db.search('KLUBAI')

def test_no_match(db):
    assert db.search('missing') == []

def test_duplicate_hash(db):
    add(db)
    with pytest.raises(ValueError): add(db,'other.txt')

def test_duplicate_name(db):
    add(db)
    with pytest.raises(ValueError): add(db,text='Different content')

def test_remove(db):
    assert db.remove_document(add(db))
    assert db.statistics() == {'documents':0,'chunks':0}
    assert db.search('KlubAI') == []

def test_missing_remove(db):
    assert not db.remove_document(999)

def test_persistence(db):
    add(db)
    assert KnowledgeDatabase(db.db_path).search('KlubAI')

def test_bad_query(db):
    with pytest.raises(ValueError): db.search('!!!')

def test_query_operators(db):
    add(db)
    assert db.search('KlubAI OR "')

def test_bad_hash(db):
    with pytest.raises(ValueError): db.add_document('a.txt','bad','TXT',1,[('a','1')])

def test_empty_chunks(db):
    with pytest.raises(ValueError): db.add_document('a.txt','a'*64,'TXT',1,[])

def test_blank_chunk(db):
    with pytest.raises(ValueError): db.add_document('a.txt','a'*64,'TXT',1,[(' ','1')])

def test_router(db):
    router = KnowledgeRouter(KnowledgeManager(db))
    assert 'Documents: 0' in router.route('/knowledge-info')
    assert router.route('Hello') is None
    assert 'Usage:' in router.route('/knowledge-remove 1')
    add(db)
    assert 'sample.txt' in router.route('/knowledge-search KlubAI')
    assert 'sample.txt' in router.route('/knowledge-list')
    assert router.route('/knowledge-remove 1 confirm') == 'Indexed document removed.'
