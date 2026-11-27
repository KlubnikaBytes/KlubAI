"""Bounded English recovery; unknown claims are not evidence of error."""
from dataclasses import dataclass
from language.response_validator import matches_language


@dataclass(frozen=True)
class RecoveryResult:
    answer: str
    outcome: str
    reasons: tuple


class ResponseRecovery:
    def __init__(self, quality, verifier, facts):
        self.quality = quality
        self.verifier = verifier
        self.facts = facts

    def reasons(self, question, answer, quality=True, verification=True):
        reasons = []
        if quality:
            report = self.quality.assess(question, answer)
            reasons.extend(i for i in report.issues if i.startswith((
                'Empty', 'Possible unfinished', 'Unclosed', 'Unexpected control', 'Repeated sentence')))
        if verification and answer.strip() and self.verifier.assess(answer).contradicted:
            reasons.append('Explicit curated contradiction')
        return tuple(reasons)

    def recover(self, question, answer, regenerate, quality=True, verification=True, facts=True):
        reasons = self.reasons(question, answer, quality, verification)
        if not reasons:
            return RecoveryResult(answer, 'unchanged', ())
        # Only replace an entire answer for an exact curated question.
        if facts and 'Explicit curated contradiction' in reasons:
            curated = self.facts.answer(question)
            if curated:
                return RecoveryResult(curated, 'curated', reasons)
        try:
            candidate = regenerate(reasons)
            if matches_language(candidate, 'en') and not self.reasons(question, candidate, quality, verification):
                # Do not treat disappearance of an exact contradiction as factual proof.
                if 'Explicit curated contradiction' not in reasons:
                    return RecoveryResult(candidate, 'regenerated', reasons)
        except (ValueError, RuntimeError):
            pass
        return RecoveryResult('I could not produce a sufficiently reliable response. Please rephrase the question or consult a trusted reference.', 'fallback', reasons)
