import pytest
from knowledge.evidence_filter import filter_evidence
from knowledge.answer_validator import validate_answer, NO_ANSWER
from knowledge.citation_manager import citation_ids

def row(name, text):
    return dict(filename=name, content=text, methods=['semantic'])

def test_entity():
    rows = [row('klubai_product.txt','KlubAI uses Python'), row('billnika_product.txt','Billnika uses Flutter')]
    assert filter_evidence('What is Billnika?', rows) == rows[1:]

def test_duplicate():
    assert len(filter_evidence('framework', [row('a.txt','Flutter framework'),row('b.txt','framework Flutter')])) == 1

def test_rank():
    rows = [row('a.txt','weather'),row('b.txt','Flutter framework')]
    assert filter_evidence('Flutter framework',rows)[0] == rows[1]

SOURCES = [{'source':1,'content':'Billnika uses Flutter.'}]

def test_exact():
    assert validate_answer('[{"source":1,"quote":"Billnika uses Flutter."}]', SOURCES) == ('Billnika uses Flutter. [1]',[1])

def test_empty():
    assert validate_answer('[]', SOURCES) == (NO_ANSWER, [])

@pytest.mark.parametrize('raw',['not json','{}','[{"source":2,"quote":"Billnika uses Flutter."}]','[{"source":1,"quote":"Billnika uses Java."}]','[{"source":true,"quote":"Billnika"}]'])
def test_invalid(raw):
    with pytest.raises(ValueError): validate_answer(raw,SOURCES)

def test_invalid_citation():
    with pytest.raises(ValueError): citation_ids('Claim [2]',SOURCES)
