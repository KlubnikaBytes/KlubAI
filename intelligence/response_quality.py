"""Heuristic English response assessment, not factual verification."""
import re
from dataclasses import dataclass
from intelligence.context_relevance import terms
from intelligence.question_classifier import QuestionClassifier


@dataclass(frozen=True)
class QualityReport:
    score: int
    components: dict
    issues: tuple
    words: int

    @property
    def rating(self):
        return next(label for threshold, label in ((90,'Excellent'),(75,'Good'),(60,'Acceptable'),(40,'Needs improvement'),(0,'Poor')) if self.score >= threshold)

    def render(self):
        return '\n'.join([f'Quality: {self.score}/100 ({self.rating})', f'Words: {self.words}', *(f'{key}: {value}' for key,value in self.components.items()), 'Issues: ' + ('; '.join(self.issues) if self.issues else 'None detected'), 'Heuristic assessment only; factual accuracy not verified.'])


class ResponseQuality:
    MAX_QUESTION = 10000
    MAX_ANSWER = 50000

    def assess(self, question, answer):
        if not isinstance(question,str) or not isinstance(answer,str):
            raise ValueError('Question and answer must be text.')
        if not question.strip() or len(question)>self.MAX_QUESTION or len(answer)>self.MAX_ANSWER:
            raise ValueError('Provide a nonempty question (max 10000 characters) and answer (max 50000 characters).')
        scores = dict(relevance=30, completeness=25, structure=20, repetition=15, length=10)
        issues = []
        words = len(re.findall(r'\b\w+\b', answer))
        def deduct(key, amount, issue):
            scores[key] = max(0, scores[key]-amount)
            issues.append(issue)
        if not words:
            return QualityReport(0, dict.fromkeys(scores,0), ('Empty or non-word response',), words)
        intent = QuestionClassifier().classify(question).intent
        q = terms(question)
        if q and intent in ('definition','factual','comparison','explanation','procedure') and not q & terms(answer):
            deduct('relevance',20,'No question keyword overlap; relevance uncertain')
        if words < 5 and intent in ('definition','explanation','comparison','procedure'):
            deduct('completeness',15,'Very short answer for explanatory question')
        if re.search(r'(?:\b(?:and|or|because|such as|including)|[:,])\s*$',answer,re.I):
            deduct('completeness',15,'Possible unfinished ending')
        if len(re.findall(r'^\s*```',answer,re.M)) % 2:
            deduct('structure',15,'Unclosed code fence')
        if re.search(r'[\x00-\x08\x0b-\x1f\x7f]',answer):
            deduct('structure',15,'Unexpected control characters')
        prose = re.sub(r'```[\s\S]*?```','',answer)
        sentences = [' '.join(re.findall(r'\w+',s.casefold())) for s in re.split(r'[.!?]+|\n+',prose)]
        sentences = [s for s in sentences if len(s.split())>=4]
        if len(sentences)!=len(set(sentences)):
            deduct('repetition',15,'Repeated sentence or line')
        if words>350 and intent in ('definition','factual'):
            deduct('length',10,'Long answer for a simple question; review requested detail')
        if re.search(r'\b(?:100% accurate|guaranteed correct|absolutely certain|without any doubt)\b',answer,re.I):
            issues.append('Strong certainty wording; evidence not verified')
        return QualityReport(sum(scores.values()),scores,tuple(issues),words)
