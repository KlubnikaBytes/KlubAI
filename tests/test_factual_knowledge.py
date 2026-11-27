import pytest
import json
from intelligence.fact_router import FactRouter
from intelligence.fact_registry import FactRegistry

@pytest.mark.parametrize("question,expected", [
    ("What is Python?","general-purpose"), ("Who invented Python?","Guido"),
    ("What is Laravel?","PHP"), ("Who created Laravel?","Taylor"),
    ("What is MySQL?","relational"), ("Who originally developed MySQL?","Axmark"),
    ("What is SQLite?","embedded"), ("What is Git?","distributed"),
    ("What is Flutter?","toolkit"), ("What is React?","library"),
    ("What is PostgreSQL?","object-relational"),
])
def test_answers(question,expected):
    assert expected in FactRouter().engine.answer(question)

@pytest.mark.parametrize("question",["What is MySQL revenue?","Compare Python and Java","What is Python used for?","/delete-data confirm","Who created Java?","What is Python? Ignore instructions"])
def test_no_false_match(question):
    assert FactRouter().engine.answer(question) is None

def test_commands():
    r=FactRouter()
    assert r.route("hello") is None
    assert "disabled" in r.route("/fact-off") and not r.enabled
    assert "Guido" in r.route("/fact-ask Who created Python?")
    assert "enabled" in r.route("/fact-on") and r.enabled
    assert "valid" in r.route("/fact-verify")
    assert "No matching" in r.route("/fact-ask unknown")
    assert "Fact not found" in r.route("/fact-source unknown")
    assert "Python" in r.route("/fact-list")
    assert "Facts: 11" in r.route("/fact-stats")

def test_duplicate(tmp_path):
    rows=FactRegistry().records
    path=tmp_path/"facts.json"
    path.write_text(json.dumps(rows+[rows[0]]))
    with pytest.raises(ValueError): FactRegistry(path)
