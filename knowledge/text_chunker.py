import unicodedata
from config import KNOWLEDGE_CHUNK_SIZE, KNOWLEDGE_CHUNK_OVERLAP

class TextChunker:
    def __init__(self, size=KNOWLEDGE_CHUNK_SIZE, overlap=KNOWLEDGE_CHUNK_OVERLAP):
        if not 0 <= overlap < size <= 10000:
            raise ValueError("Invalid chunk configuration.")
        self.size, self.overlap = size, overlap

    def split(self, text):
        text = ''.join(c if c in '\n\t' or not unicodedata.category(c).startswith('C') else ' ' for c in text)
        text = text.strip()
        chunks = []
        start = 0
        while start < len(text):
            end = min(start + self.size, len(text))
            content = text[start:end].strip()
            if content:
                chunks.append((content, f"Extracted text characters {start+1}-{end}"))
            if end == len(text):
                break
            start = end - self.overlap
        return chunks
