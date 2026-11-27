from intelligence.fact_registry import FactRegistry
from intelligence.fact_matcher import FactMatcher

class FactualKnowledge:
    def __init__(self, registry=None):
        self.registry = registry or FactRegistry()
        self.matcher = FactMatcher(self.registry)

    @staticmethod
    def render(row):
        return f"{row['answer']}\n\nCurated local reference: {row['publisher']}\n{row['url']}\nFact ID: {row['id']}"

    def answer(self, question):
        row = self.matcher.match(question)
        return self.render(row) if row else None
