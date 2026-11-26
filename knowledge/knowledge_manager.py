from config import KNOWLEDGE_DOCUMENTS_DIR
from knowledge.knowledge_database import KnowledgeDatabase
from knowledge.document_ingestor import DocumentIngestor
from knowledge.embedding_store import EmbeddingStore


class KnowledgeManager:

    def __init__(
        self,
        database=None,
        directory=KNOWLEDGE_DOCUMENTS_DIR,
    ):
        self.database = (
            database
            if database is not None
            else KnowledgeDatabase()
        )

        self.ingestor = DocumentIngestor(
            self.database,
            directory,
        )

    def embedding_store(self):
        if not hasattr(self, "_embedding_store"):
            self._embedding_store = EmbeddingStore(self.database)
        return self._embedding_store

    def list_documents(self):
        return self.database.list_documents()

    def statistics(self):
        return self.database.statistics()

    def search(self, query):
        return self.database.search(query)

    def remove_document(self, document_id):
        return self.database.remove_document(
            document_id
        )

    def list_files(self):
        return self.ingestor.list_files()

    def ingest(self, filename):
        return self.ingestor.ingest(filename)

    def ingest_all(self):
        return self.ingestor.ingest_all()
