"""Conservative English intent labels; never authorize or execute actions."""
import re
from dataclasses import dataclass


@dataclass(frozen=True)
class Classification:
    intent: str
    reason: str


class QuestionClassifier:
    MAX_LENGTH = 10000
    RULES = (
        ("greeting", r"(?:hello|hi|hey|good morning|good evening|how are you)[.!?]*$"),
        ("identity", r"(?:who are you|who developed you|what is your name)[.!?]*$"),
        ("memory_retrieval", r"(?:what is my|what's my|do you remember my|recall my)\b"),
        ("memory_storage", r"(?:remember that|my (?:name|favourite colour|favorite color|company) is)\b"),
        ("file_generation", r"(?:create|generate|make|prepare|write)\s+(?:(?:a|an)\s+)?(?:pdf|word|docx|excel|xlsx|csv|txt|text|powerpoint|pptx)\b"),
        ("calculation", r"(?:calculate|compute|convert)\b|\d+(?:\.\d+)?\s*[+*/×÷-]\s*\d+"),
        ("document_analysis", r"(?:read|summarize|analyse|analyze)\s+.+\.(?:pdf|docx|xlsx|csv|txt|md|json|pptx)$"),
        ("product_knowledge", r"(?:what is|tell me about|explain|about)\s+(?:billnika|klubai)\b"),
        ("follow_up", r"(?:explain (?:it|that|this)|tell me more|continue|give more details|make it|why is that)\b"),
        ("comparison", r"(?:compare|difference between|what is the difference between)\b"),
        ("programming", r"(?:write|generate|create|fix|debug)\s+.*\b(?:code|function|script|program|class|query)\b"),
        ("procedure", r"(?:how to|how (?:do|can|should) i|steps to)\b"),
        ("explanation", r"(?:how (?:does|do|is|are)|why|explain)\b"),
        ("definition", r"(?:what is|what are|define|what's)\b"),
        ("factual", r"(?:who|when|where|which|how many|how much|what)\b"),
        ("writing", r"(?:write|draft|rewrite|compose)\b"),
    )

    def classify(self, text):
        if not isinstance(text, str):
            raise TypeError("Input must be text.")
        if len(text) > self.MAX_LENGTH:
            raise ValueError("Classification input exceeds 10000 characters.")
        normalized = " ".join(text.casefold().split())
        if not normalized:
            return Classification("empty", "No input")
        if re.match(r"^/[a-z][a-z0-9-]*(?:\s|$)", normalized):
            return Classification("command", "Slash command syntax")
        if re.search(r"[\u0900-\u097f]", normalized):
            from intelligence.hindi_question_classifier import HindiQuestionClassifier
            return HindiQuestionClassifier().classify(text)
        for intent, pattern in self.RULES:
            if re.match(pattern, normalized):
                return Classification(intent, "Matched English intent pattern")
        return Classification("unknown", "No supported intent pattern matched")
