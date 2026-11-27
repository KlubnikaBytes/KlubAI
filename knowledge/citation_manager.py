import re
from knowledge.knowledge_router import safe_display

def citation_ids(answer, sources):
    ids = [int(x) for x in re.findall(r'\[([0-9]{1,6})\]', answer)]
    allowed = {s['source'] for s in sources}
    if not ids or any(i not in allowed for i in ids):
        raise ValueError('Missing or invalid citation.')
    return list(dict.fromkeys(ids))

def render_sources(ids, sources):
    return '\n'.join(f"[{s['source']}] {safe_display(s['filename'])} | {safe_display(s['location'])}" for s in sources if s['source'] in ids)
