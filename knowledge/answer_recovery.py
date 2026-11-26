import json
import re
from knowledge.answer_validator import validate_answer

def validate_recovered(raw, sources):
    raw = raw.strip()
    fence = re.fullmatch(r'```(?:json)?\s*(.*?)\s*```', raw, re.S | re.I)
    if fence: raw = fence.group(1)
    data = json.loads(raw)
    if isinstance(data, list):
        lookup = {s['source']:s['content'] for s in sources}
        for item in data:
            if not isinstance(item, dict) or type(item.get('source')) is not int or not isinstance(item.get('quote'), str):
                continue
            text = lookup.get(item['source'], '')
            quote = item['quote'].strip()
            if quote and quote not in text:
                pattern = r'\s+'.join(re.escape(word) for word in quote.split())
                match = re.search(pattern, text)
                if match: item['quote'] = match.group()
    return validate_answer(json.dumps(data), sources)
