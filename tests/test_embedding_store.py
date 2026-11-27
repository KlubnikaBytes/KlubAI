import numpy as np
from knowledge.knowledge_database import KnowledgeDatabase
from knowledge.embedding_store import EmbeddingStore
from knowledge.embedding_engine import EmbeddingEngine

class FakeBackend:
    def embed(self,texts,batch_size=16): return [np.ones(384) for _ in texts]

def test_lifecycle(tmp_path):
    db=KnowledgeDatabase(tmp_path/'knowledge.db')
    doc=db.add_document('a.txt','a'*64,'TXT',4,[('text','1')])
    store=EmbeddingStore(db,EmbeddingEngine(FakeBackend()))
    assert store.statistics()['pending']==1
    assert store.build()==1
    assert store.build()==0
    assert EmbeddingStore(db).statistics()['indexed']==1
    with db.connect() as conn:
        conn.execute("UPDATE knowledge_chunks SET content='changed'")
    assert store.statistics()['pending']==1
    assert store.build()==1
    db.remove_document(doc)
    assert store.statistics()==dict(total=0,indexed=0,pending=0)
