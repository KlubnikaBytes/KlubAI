import pytest
from intelligence.question_classifier import QuestionClassifier
from intelligence.intelligence_router import IntelligenceRouter


@pytest.mark.parametrize("text,expected", [
    ("Hello!", "greeting"), ("Who are you?", "identity"),
    ("What is Python?", "definition"), ("Who invented Python?", "factual"),
    ("How does Laravel work?", "explanation"), ("How to install Flutter?", "procedure"),
    ("Compare Python and Java", "comparison"), ("Write Python code for a calculator", "programming"),
    ("Calculate 25 x 16", "calculation"), ("25 * 16", "calculation"),
    ("Create a PDF about AI", "file_generation"), ("What is my favourite colour?", "memory_retrieval"),
    ("What is Billnika?", "product_knowledge"), ("Explain it in more detail", "follow_up"),
    ("/knowledge-status", "command"), ("/delete-data confirm", "command"),
    ("My name is Sam", "memory_storage"), ("Summarize sample.txt", "document_analysis"),
    ("Draft an email", "writing"), ("", "empty"), ("xyz", "unknown"),
    ("  WHAT   IS Python?  ", "definition"), ("Python क्या है?", "unknown"),
])
def test_intent(text, expected):
    assert QuestionClassifier().classify(text).intent == expected


def test_invalid():
    with pytest.raises(TypeError):
        QuestionClassifier().classify(None)
    with pytest.raises(ValueError):
        QuestionClassifier().classify("x" * 10001)


def test_router():
    router = IntelligenceRouter()
    assert "Intent: command" in router.route("/classify /delete-data confirm")
    assert "Usage:" in router.route("/classify")
    assert "observation only" in router.route("/intelligence-info")
    assert "/classify" in router.route("/intelligence-help")
    assert router.route("/calculate 2+2") is None
    assert router.route("What is Python?") is None
    assert "Invalid" in router.route("/intelligence-unknown")
    assert "exceeds" in router.route("/classify " + "x" * 10001)
