import pytest
from knowledge.text_chunker import TextChunker

def test_overlap():
    chunks = TextChunker(10, 3).split('abcdefghijklmnopqrstuvwxyz')
    assert chunks[0][0][-3:] == chunks[1][0][:3]
    assert all(len(c) <= 10 for c, _ in chunks)

def test_empty():
    assert TextChunker().split('  ') == []

def test_controls():
    assert '\x1b' not in TextChunker().split('hello\x1bworld')[0][0]

@pytest.mark.parametrize('size,overlap', [(0,0),(10,10),(10,-1)])
def test_invalid(size, overlap):
    with pytest.raises(ValueError): TextChunker(size, overlap)
