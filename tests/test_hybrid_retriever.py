from knowledge.hybrid_retriever import HybridRetriever
from tests.test_vector_search import setup


def test_combined(setup):
    db,store,search=setup
    store.build()
    results=HybridRetriever(db,search).search('billing')
    assert len(results)==1
    assert results[0]['methods']==['keyword','semantic']
    assert results[0]['score']==2/61


def test_semantic_only(setup):
    db,store,search=setup
    store.build()
    assert HybridRetriever(db,search).search('tax')[0]['methods']==['semantic']


def test_keyword_only(setup):
    db,store,search=setup
    assert HybridRetriever(db,search).search('billing')[0]['methods']==['keyword']


def test_no_match(setup):
    db,store,search=setup
    assert HybridRetriever(db,search).search('unknown')==[]
