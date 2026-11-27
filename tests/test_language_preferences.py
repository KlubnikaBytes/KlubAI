import pytest
from memory.database import Database
from language.language_preferences import LanguagePreferences
from language.language_router import LanguageRouter

@pytest.fixture
def prefs(tmp_path):
    return LanguagePreferences(Database(tmp_path / "test.db"))

def test_default(prefs):
    assert prefs.get() == "auto"

@pytest.mark.parametrize("code", ["en", "hi", "bn", "hinglish", "auto"])
def test_persistence(prefs, code):
    prefs.set(code)
    assert LanguagePreferences(Database(prefs.database.db_path)).get() == code

def test_invalid(prefs):
    with pytest.raises(ValueError):
        prefs.set("invalid")
    assert prefs.get() == "auto"

def test_reset(prefs):
    prefs.set("hi")
    prefs.database.save_memory("colour", "green")
    prefs.reset()
    assert prefs.get() == "auto"
    assert prefs.database.get_memory("colour") == "green"

def test_delete_data(prefs):
    prefs.set("bn")
    prefs.database.clear_all_data()
    assert prefs.get() == "auto"

def test_router(prefs):
    router = LanguageRouter(preferences=prefs)
    assert "saved: hi" in router.route("/language hi")
    assert "hi" in router.route("/language")
    assert "Unsupported" in router.route("/language invalid")
    assert "reset: auto" in router.route("/language-reset")
    assert router.route("/gst 100 18") is None
