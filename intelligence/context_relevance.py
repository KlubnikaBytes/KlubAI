"""Local lexical relevance filtering; no database writes or model calls."""
import re
from dataclasses import dataclass
from intelligence.question_classifier import QuestionClassifier

STOP = set('a an the is are was were what who when where which why how to of in on for and or with about me you your my it this that these those do does can could please tell explain define more detail details give show write'.split())


def terms(text):
    return set(re.findall(r'[a-z0-9]+', text.casefold())) - STOP


@dataclass(frozen=True)
class Selection:
    messages: list
    scores: tuple
    reason: str


class ContextRelevance:
    def select(self, messages, enabled=True):
        if len(messages) < 2 or messages[0]['role'] != 'system' or messages[-1]['role'] != 'user':
            raise ValueError('Expected system and latest user messages.')
        copied = [dict(m) for m in messages]
        history = copied[1:-1]
        if history and history[0]['role'] == 'assistant':
            history = history[1:]
        if len(history) % 2 or any(m['role'] != ('user' if i % 2 == 0 else 'assistant') for i,m in enumerate(history)):
            return Selection(copied, (), 'Unexpected history structure; unchanged')
        pairs = list(zip(history[::2], history[1::2]))
        question = copied[-1]['content']
        if not enabled or not question.isascii() or len(question) > 10000:
            return Selection(copied, (), 'Filtering disabled or unsupported input; unchanged')
        intent = QuestionClassifier().classify(question).intent
        q = terms(question)
        follow = intent == 'follow_up' or bool(re.search(r'\b(it|that|this|they|them|its|those|these|previous|above|same|earlier)\b', question.lower()))
        if follow or not q or intent == 'unknown':
            return Selection(copied, (), 'Follow-up or uncertain intent; preserve compatible history')
        scores = []
        kept = []
        for i,(user,answer) in enumerate(pairs):
            u = terms(user['content']); a = terms(answer['content'])
            overlap = len(q & u) / len(q)
            # Answer-only matches require two distinct terms to reduce incidental matches.
            related = bool(q & u) or len(q & a) >= 2
            score = round(overlap + .25 * len(q & a)/len(q) + .05*(i+1)/max(1,len(pairs)), 3)
            scores.append((i+1, score, related))
            if related:
                kept.extend((user,answer))
        return Selection([copied[0], *kept, copied[-1]], tuple(scores), 'Lexical relevance; chronological order preserved')
