import hashlib
from config import KNOWLEDGE_DOCUMENTS_DIR
from tools.file_reader import FileReader
from knowledge.text_chunker import TextChunker

class DocumentIngestor:
    def __init__(self, database, directory=KNOWLEDGE_DOCUMENTS_DIR):
        self.database = database
        self.reader = FileReader(directory)
        self.chunker = TextChunker()

    def list_files(self):
        return self.reader.list_files()

    def ingest(self, filename):
        path = self.reader.validator.validate(filename)
        data = path.read_bytes()
        digest = hashlib.sha256(data).hexdigest()
        result = self.reader.read(path.name)
        if hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            raise ValueError("Document changed during import; retry.")
        if result['truncated']:
            raise ValueError("Document exceeds extraction limits; split it into smaller files.")
        chunks = self.chunker.split(result['content'])
        if not chunks or not any(c.isalnum() for c in result['content']):
            raise ValueError("No readable text found; OCR may be required.")
        document_id = self.database.add_document(path.name, digest, result['format'], len(data), chunks)
        return {'id': document_id, 'filename': path.name, 'chunks': len(chunks)}

    def ingest_all(self):
        results = []
        for item in self.list_files():
            try:
                results.append(self.ingest(item['name']))
            except Exception as error:
                results.append({'filename': item['name'], 'error': str(error) if isinstance(error, ValueError) else type(error).__name__})
        return results
