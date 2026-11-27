from knowledge.entity_detector import detect_entities, tokens

STOP = set('what which who how does do is are was were the a an of in on for to and or can could about support supports used use available main many much'.split())

def filter_evidence(question, rows):
    rows = [r for r in rows if 'semantic' in r.get('methods', [])]
    entities = detect_entities(question, rows)
    terms = set(tokens(question)) - STOP - entities
    ranked = []
    for i, row in enumerate(rows):
        words = set(tokens(row['content']))
        if entities and not entities.intersection(words):
            continue
        overlap = len(terms & words)
        ranked.append((overlap, i, row, words))
    ranked.sort(key=lambda x: (-x[0], x[1]))
    selected, seen = [], []
    for _, _, row, words in ranked:
        if any(words == old or len(words & old) / max(1, len(words | old)) >= .75 for old in seen):
            continue
        selected.append(row)
        seen.append(words)
    return selected
