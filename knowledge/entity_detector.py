import re
from pathlib import Path

def tokens(text):
    return re.findall(r'[^\W_]+', text.casefold())

def detect_entities(question, rows):
    # Infer explicit subjects from product/document names, not a fixed product list.
    words = set(tokens(question))
    generic = {'product', 'documentation', 'knowledge', 'report', 'sample', 'test', 'guide', 'manual', 'about', 'what', 'how', 'which', 'the', 'features'}
    return {tokens(Path(r['filename']).stem)[0] for r in rows
            if tokens(Path(r['filename']).stem) and tokens(Path(r['filename']).stem)[0] in words - generic}
