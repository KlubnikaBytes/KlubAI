import pytest
from intelligence.hindi_question_classifier import HindiQuestionClassifier
from intelligence.question_classifier import QuestionClassifier
from intelligence.intelligence_router import IntelligenceRouter
from language.language_router import LanguageRouter


@pytest.mark.parametrize('text,expected', [
    ('नमस्ते', 'greeting'), ('आप कौन हैं?', 'identity'),
    ('पायथन क्या है?', 'definition'), ('Python क्या है?', 'definition'),
    ('पायथन का आविष्कार किसने किया?', 'factual'),
    ('पायथन कैसे सीखें?', 'procedure'), ('पायथन के फायदे बताइए।', 'explanation'),
    ('Python और Java में क्या अंतर है?', 'comparison'),
    ('एक Python प्रोग्राम लिखिए।', 'programming'),
    ('२५ गुणा १६ कितना होगा?', 'calculation'),
    ('मेरा पसंदीदा रंग क्या है?', 'memory_retrieval'),
    ('मेरा नाम राहुल है।', 'memory_storage'),
    ('Billnika की विशेषताएँ बताइए।', 'product_knowledge'),
    ('इसके बारे में और बताइए।', 'follow_up'),
    ('एक PDF रिपोर्ट बनाइए।', 'file_generation'),
    ('sample.pdf का सारांश बताइए।', 'document_analysis'),
    ('एक पत्र लिखिए।', 'writing'), ('आज मौसम सुहावना है।', 'unknown'),
    ('/delete-data confirm', 'command'), ('', 'empty'),
])
def test_hindi(text, expected):
    assert HindiQuestionClassifier().classify(text).intent == expected
    assert QuestionClassifier().classify(text).intent == expected


def test_bounds():
    with pytest.raises(ValueError):
        HindiQuestionClassifier().classify('क' * 10001)
    with pytest.raises(TypeError):
        HindiQuestionClassifier().classify(None)


def test_routers():
    router = LanguageRouter()
    assert 'Intent: command' in router.route('/hindi-classify /delete-data confirm')
    assert 'Intent: definition' in router.route('/hindi-classify Python क्या है?')
    assert 'Use /hindi-help' in router.route('/hindi-classify')
    assert 'Intent: definition' in IntelligenceRouter().route('/classify Python क्या है?')
    assert QuestionClassifier().classify('What is Python?').intent == 'definition'


@pytest.mark.parametrize("text", [
    "२५ + ७५",
    "१०० - २५",
    "२५ × १६",
    "१०० ÷ ४",
    "१२.५० + ७.५०",
    "२५ * 16",
    "25 + 75",
    "१० + २० + ३०",
])
def test_normalized_numeric_expression(text):
    assert (
        HindiQuestionClassifier().classify(text).intent
        == "calculation"
    )

    assert (
        QuestionClassifier().classify(text).intent
        == "calculation"
    )


@pytest.mark.parametrize("text", [
    "१२३४५",
    "१२.५०",
    "2026",
])
def test_number_only_is_not_calculation(text):
    assert (
        HindiQuestionClassifier().classify(text).intent
        == "unknown"
    )    
