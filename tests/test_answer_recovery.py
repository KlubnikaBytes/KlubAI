import json
from pathlib import Path
import pytest
from knowledge.evidence_selector import select_evidence
from knowledge.answer_recovery import validate_recovered
from knowledge.answer_validator import validate_answer, NO_ANSWER

B = '# Product\n\nAlpha is a billing application\ndeveloped by Example.\n\nAlpha uses Flutter.\n\n## Sales Management\n\nSales Invoice\n\n## Inventory Management\n\nStock Management'
K = '# Product\n\nBeta is an assistant developed by Example.\n\nBeta uses Python.\n\nBeta supports persistent memory.\n\nBeta can generate PDF files.\n\nExternal AI APIs are not required.'
S = [dict(source=1,filename='alpha_product.txt',content=B),dict(source=2,filename='beta_product.txt',content=K)]
@pytest.mark.parametrize('question,expected', [('What is Alpha?','billing application'),('Which technologies are used in Alpha?','Flutter'),('Who developed Beta?','developed by Example'),('Does Beta support persistent memory?','persistent memory'),('Which file formats can Beta generate?','PDF'),('Does Beta require external AI APIs?','not required'),('Which sales transactions are supported by Alpha?','Sales Invoice'),('What are the main features of Alpha?','Stock Management'),('Which technologies are used in Alpha and Beta?','Python')])
def test_selection(question,expected):
    answer, ids = validate_answer(json.dumps(select_evidence(question,S)),S)
    assert expected in answer and ids
    if 'sales transactions' in question: assert 'Stock Management' not in answer
    if 'Alpha and Beta' in question: assert ids == [1,2]

def test_unknown():
    assert select_evidence('What is the annual revenue of Alpha?',S)==[]

def test_whitespace():
    answer,ids=validate_recovered('```json\n[{"source":1,"quote":"Alpha is a billing application developed by Example."}]\n```',S)
    assert 'application\ndeveloped' in answer and ids==[1]

def test_invented():
    with pytest.raises(ValueError): validate_recovered('[{"source":1,"quote":"Alpha uses Java."}]',S)
