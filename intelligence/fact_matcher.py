import re

class FactMatcher:
    def __init__(self, registry):
        self.registry = registry

    def match(self, question):
        q = " ".join(question.casefold().split()).rstrip("?.!")
        if len(q)>1000:
            return None
        for row in self.registry.records:
            entity = re.escape(row["entity"].casefold())
            patterns = ([rf"what is {entity}", rf"define {entity}"] if row["predicate"] == "definition" else [rf"who (?:originally )?(?:created|developed|invented) {entity}", rf"who is the creator of {entity}"])
            if any(re.fullmatch(pattern,q) for pattern in patterns):
                return row
        return None
