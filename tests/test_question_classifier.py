
import pytest

from intelligence.question_classifier import QuestionClassifier


@pytest.mark.parametrize("text,expected", [
    ("Hello!", "greeting"),
    ("Who are you?", "identity"),
    ("What is Python?", "definition"),
    ("Who invented Python?", "factual"),
    ("How does Laravel work?", "explanation"),
    ("How to install Flutter?", "procedure"),
    ("Compare Python and Java", "comparison"),
    ("Write Python code for a calculator", "programming"),
    ("Calculate 25 x 16", "calculation"),
    ("25 * 16", "calculation"),
    ("Create a PDF about AI", "file_generation"),
    ("What is my favourite colour?", "memory_retrieval"),
    ("What is Billnika?", "product_knowledge"),
    ("Explain it in more detail", "follow_up"),
    ("/knowledge-status", "command"),
    ("/delete-data confirm", "command"),
    ("My name is Sam", "memory_storage"),
    ("Summarize sample.txt", "document_analysis"),
    ("Draft an email", "writing"),
    ("", "empty"),
    ("xyz", "unknown"),
    ("  WHAT   IS Python?  ", "definition"),

    # Phase 8D.2: Mixed Hindi-English classification
    ("Python क्या है?", "definition"),
])
def test_intent(text, expected):
    assert QuestionClassifier().classify(text).intent == expected


def test_invalid_input():
    with pytest.raises(TypeError):
        QuestionClassifier().classify(None)


def test_long_input():
    with pytest.raises(ValueError):
        QuestionClassifier().classify("a" * 10001)
