import numpy as np
import pytest
from knowledge.knowledge_database import KnowledgeDatabase
from knowledge.embedding_store import EmbeddingStore
from knowledge.embedding_engine import EmbeddingEngine
from knowledge.vector_search import VectorSearch

class Backend:
    def embed(self, texts, batch_size=16):
        return [np.eye(1,384,0 if 'tax' in t or 'billing' in t else 1)[0] for t in texts]

@pytest.fixture
def setup(tmp_path):
    db=KnowledgeDatabase(tmp_path/'db.sqlite')
    db.add_document('billing.txt','a'*64,'TXT',7,[('billing','1')])
    db.add_document('weather.txt','b'*64,'TXT',7,[('weather','1')])
    store=EmbeddingStore(db,EmbeddingEngine(Backend()))
    return db,store,VectorSearch(store)

def test_empty(setup):
    assert setup[2].search('tax') == []

def test_rank(setup):
    db,store,search=setup
    store.build()
    assert search.search('tax')[0]['filename']=='billing.txt'
    assert search.search('tax')[0]['score']==pytest.approx(1)

def test_threshold(setup):
    setup[1].build()
    assert len(setup[2].search('tax'))==1
    assert len(setup[2].search('tax',min_score=0))==2

def test_limit(setup):
    setup[1].build()
    assert len(setup[2].search('tax',limit=1,min_score=0))==1

@pytest.mark.parametrize('query',['','!!!','x'*1001])
def test_invalid(setup,query):
    with pytest.raises(ValueError): setup[2].search(query)

def test_remove(setup):
    db,store,search=setup
    store.build()
    db.remove_document(1)
    assert search.search('tax')==[]
