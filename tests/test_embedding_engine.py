import numpy as np
import pytest
from knowledge.embedding_engine import EmbeddingEngine

class FakeBackend:
    def embed(self, texts, batch_size=16):
        return [np.ones(384) for _ in texts]

def test_normalized():
    vectors = EmbeddingEngine(FakeBackend()).embed(['one','two'])
    assert vectors.shape == (2,384)
    assert np.allclose(np.linalg.norm(vectors,axis=1),1)

@pytest.mark.parametrize('texts',[[],[' ']])
def test_empty(texts):
    with pytest.raises(ValueError): EmbeddingEngine(FakeBackend()).embed(texts)

@pytest.mark.parametrize('vector',[np.zeros(384),np.ones(3),np.full(384,np.nan)])
def test_invalid(vector):
    class Bad:
        def embed(self,texts,batch_size=16): return [vector]
    with pytest.raises(ValueError): EmbeddingEngine(Bad()).embed(['text'])
