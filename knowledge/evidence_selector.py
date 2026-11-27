"""Conservative extractive selection for common English document questions."""
import re
from pathlib import Path
from knowledge.entity_detector import tokens

RULES = [
 ('unknown', r'\b(revenue|subscription price|customers|pricing|salary|profit)\b', r'\b(revenue|price|pricing|customers|salary|profit)\b'),
 ('technology', r'\b(technologies|technology|tech stack|frameworks?)\b', r'\b(uses|built with|powered by)\b'),
 ('developer', r'\b(who developed|developer|created by)\b', r'\b(developed by|created by)\b'),
 ('api', r'\bexternal\b.*\bapis?\b', r'\bexternal\b.*\bapis?\b'),
 ('memory', r'\bpersistent memory\b', r'\bpersistent memory\b'),
 ('sales', r'\bsales\b', r'^##\s+sales\b'),
 ('purchase', r'\bpurchase\b', r'^##\s+purchase\b'),
 ('inventory', r'\b(inventory|stock)\b', r'^##\s+inventory\b'),
 ('financial', r'\b(financial|receivable|payable)\b', r'^##\s+financial\b'),
 ('documents', r'\b(file formats|documents.*generate|generate.*files)\b', r'^##\s+document generation\b|\bcan generate\b'),
 ('features', r'\b(features|capabilities)\b', r'^##\s+(sales|purchase|inventory|financial|document generation)\b|\bsupports\b|\bcan generate\b'),
 ('intro', r'\b(what is|difference between|compare)\b', r'\bis (?:a|an)\b'),
]

def blocks(text):
    # Preserve original whitespace and section boundaries.
    for section in re.split(r'(?m)(?=^##\s)', text):
        if section.startswith('## '):
            yield section.strip()
        else:
            for paragraph in re.split(r'\n\s*\n', section):
                paragraph = paragraph.strip()
                if paragraph and not paragraph.startswith('#'):
                    yield paragraph

def select_evidence(question, sources):
    q = question.casefold()
    rule = next((r for r in RULES if re.search(r[1], q)), None)
    if rule is None:
        return None
    subjects = set(tokens(question))
    generic = {'sample','test','report','product','documentation','knowledge','guide','manual'}
    named = {tokens(Path(s['filename']).stem)[0] for s in sources if tokens(Path(s['filename']).stem)} & subjects - generic
    if rule[0] == 'intro' and not (re.search(r'\b(difference between|compare)\b', q) or any(re.fullmatch(r'what is '+re.escape(n)+r'\s*\??', q.strip()) for n in named)):
        return []
    result = []
    covered = set()
    for s in sources:
        name = tokens(Path(s['filename']).stem)
        if named and (not name or name[0] not in named):
            continue
        for block in blocks(s['content']):
            normalized = re.sub(r'\s+', ' ', block).casefold()
            target = block.casefold() if block.startswith('## ') else normalized
            if not re.search(rule[2], target):
                continue
            # A mention of pricing etc. is not proof of a requested numeric fact.
            if rule[0] == 'unknown':
                continue
            if len(block) > 1500 or any(block == x['quote'] for x in result):
                continue
            result.append({'source':s['source'], 'quote':block})
            if name: covered.add(name[0])
    if named - covered:
        return []
    return result[:8]
