from knowledge.knowledge_database import KnowledgeDatabase


class KnowledgeManager:
    def __init__(self, database=None):
        self.database = database if database is not None else KnowledgeDatabase()

    def list_documents(self):
        return self.database.list_documents()

    def statistics(self):
        return self.database.statistics()

    def search(self, query):
        return self.database.search(query)

    def remove_document(self, document_id):
        return self.database.remove_document(document_id)
