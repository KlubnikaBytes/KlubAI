"""Isolated local component checks and optional raw model evaluation."""
import json
import time
from datetime import datetime, timezone
from uuid import uuid4
from config import APP_VERSION, DATASETS_DIR
from intelligence.question_classifier import QuestionClassifier
from intelligence.context_relevance import ContextRelevance
from intelligence.response_quality import ResponseQuality
from intelligence.answer_verifier import AnswerVerifier
from intelligence.factual_knowledge import FactualKnowledge
from intelligence.response_recovery import ResponseRecovery
from tools.calculator import Calculator
from language.response_validator import matches_language


class BenchmarkEngine:
    def __init__(self, model, dataset=None):
        self.model = model
        self.dataset = dataset or DATASETS_DIR / 'intelligence_benchmark.json'

    def run(self, suite):
        if suite not in ('components', 'model'):
            raise ValueError('Choose components or model.')
        cases = json.loads(self.dataset.read_text(encoding='utf8'))
        facts = FactualKnowledge()
        quality = ResponseQuality()
        verifier = AnswerVerifier(facts.registry)
        recovery = ResponseRecovery(quality, verifier, facts)
        rows = []
        for case in cases:
            kind = case['kind']
            if (kind == 'model') != (suite == 'model'):
                continue
            q = case['question']; expected = case['expected']
            start = time.perf_counter()
            status = 'error'
            try:
                if kind == 'intent': actual = QuestionClassifier().classify(q).intent
                elif kind == 'math': actual = str(Calculator().calculate(q))
                elif kind == 'fact': actual = (facts.answer(q) or '').split('\n')[0]
                elif kind == 'quality': actual = bool(quality.assess(q, case['answer']).issues)
                elif kind == 'verify':
                    r = verifier.assess(case['answer']); actual = [r.supported, r.contradicted, r.unverified]
                elif kind == 'recovery': actual = recovery.recover(q, case['answer'], lambda _: case['candidate']).outcome
                elif kind == 'context':
                    messages = [{'role':'system','content':'Test'}, *case['history'], {'role':'user','content':q}]
                    actual = (len(ContextRelevance().select(messages).messages)-2)//2
                elif kind == 'model':
                    stream = self.model.stream_response([{'role':'system','content':'Answer accurately and briefly in English.'},{'role':'user','content':q}], temperature=0.2)
                    try: actual = ''.join(stream).strip()
                    finally: stream.close()
                else: raise ValueError('Unknown case kind')
                status = 'manual_review' if kind == 'model' else ('pass' if actual == expected else 'fail')
            except Exception as error:
                actual = type(error).__name__
            row = dict(id=case['id'], kind=kind, question=q, expected=expected, actual=actual, status=status, seconds=round(time.perf_counter()-start,4))
            if kind == 'model' and status == 'manual_review': row['language_compliant'] = matches_language(actual,'en')
            rows.append(row)
        return dict(id=uuid4().hex, timestamp=datetime.now(timezone.utc).isoformat(), version=APP_VERSION, model=self.model.model_id, suite=suite, rows=rows)
