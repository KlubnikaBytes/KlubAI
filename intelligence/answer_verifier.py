"""Conservative local pattern checks, not general factual entailment."""
import re
from dataclasses import dataclass
from intelligence.fact_registry import FactRegistry


def normalize(text):
    return ' '.join(text.casefold().strip().rstrip('.!?').split())


@dataclass(frozen=True)
class VerificationReport:
    supported: int
    contradicted: int
    unverified: int
    known_urls: int
    unknown_urls: int
    fact_ids: tuple

    def render(self):
        return (f'Supported: {self.supported}\nContradicted: {self.contradicted}\n'
                f'Unverified: {self.unverified}\nKnown reference URLs: {self.known_urls}\n'
                f'Unknown reference URLs: {self.unknown_urls}\n'
                f'Fact IDs: {", ".join(self.fact_ids) or "none"}\n'
                'Local pattern assessment only; not proof of truth or live citation verification.')


class AnswerVerifier:
    def __init__(self, registry=None):
        self.registry = registry or FactRegistry()

    def assess(self, answer):
        if not isinstance(answer, str) or not answer.strip() or len(answer)>20000:
            raise ValueError('Provide nonempty answer text of at most 20000 characters.')
        urls = re.findall(r'https?://[^\s<>"`]+', answer)
        urls = [u.rstrip('.,;)') for u in urls]
        known = {r['url'] for r in self.registry.records}
        # Code and reference metadata are not treated as factual prose.
        prose = re.sub(r'```[\s\S]*?```', '\n[code omitted]\n', answer)
        prose = re.sub(r'https?://[^\s<>"`]+', '', prose)
        claims = [normalize(s) for s in re.split(r'(?<=[.!?])\s+|\n+', prose) if s.strip()]
        counts = dict(supported=0, contradicted=0, unverified=0)
        ids = set()
        for claim in claims:
            status = 'unverified'
            for row in self.registry.records:
                fact = normalize(row['answer'])
                if claim == fact:
                    status = 'supported'
                else:
                    # Only explicit negation of the exact curated statement.
                    negated = re.sub(r'\b(is|was)\b', r'\1 not', fact, count=1)
                    if negated != fact and claim == negated:
                        status = 'contradicted'
                if status != 'unverified':
                    ids.add(row['id'])
                    break
            counts[status] += 1
        return VerificationReport(**counts, known_urls=sum(u in known for u in urls), unknown_urls=sum(u not in known for u in urls), fact_ids=tuple(sorted(ids)))
