import json
import re
from knowledge.citation_manager import citation_ids

NO_ANSWER = 'The available knowledge does not contain enough relevant evidence.'

def validate_answer(raw, sources):
    # Extractive output: the model selects verbatim evidence, not free-form claims.
    data = json.loads(raw.strip())
    if not isinstance(data, list) or len(data) > 8:
        raise ValueError('Expected a list of evidence selections.')
    lookup = {s['source']: s['content'] for s in sources}
    lines = []
    for item in data:
        if not isinstance(item, dict) or set(item) != {'source', 'quote'}:
            raise ValueError('Invalid evidence selection.')
        sid, quote = item['source'], item['quote']
        if type(sid) is not int or sid not in lookup or not isinstance(quote, str):
            raise ValueError('Invalid source.')
        quote = quote.strip()
        if not quote or len(quote) > 1500 or quote not in lookup[sid]:
            raise ValueError('Quote does not match source.')
        line = f'{quote} [{sid}]'
        if line not in lines:
            lines.append(line)
    if not lines:
        return NO_ANSWER, []
    answer = '\n\n'.join(lines)
    return answer, citation_ids(answer, sources)
