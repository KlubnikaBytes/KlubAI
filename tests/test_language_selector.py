import pytest
from language.language_selector import LanguageSelector

@pytest.mark.parametrize("detected,expected", [("en","en"),("hi","hi"),("bn","bn"),("hinglish","hinglish"),("mixed-hi","hi"),("mixed-bn","bn"),("unknown","en"),("mixed","en")])
def test_auto(detected, expected):
    assert LanguageSelector().select("auto", detected) == expected

def test_manual():
    assert LanguageSelector().select("bn", "en") == "bn"

def test_neutral():
    s = LanguageSelector()
    s.select("auto", "hi")
    assert s.select("auto", "neutral") == "hi"
    s.reset()
    assert s.select("auto", "neutral") == "en"
