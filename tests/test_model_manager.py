import pytest
from core import model_registry
from core.model_manager import ModelManager
from memory.database import Database

class FakeEngine:
    model_id = "1.7b"
    loaded = True
    fail = None
    def is_loaded(self): return self.loaded
    def close(self): self.loaded = False
    def load_model(self):
        assert not self.loaded
        if self.model_id == self.fail: raise RuntimeError("test failure")
        self.loaded = True

@pytest.fixture
def manager(tmp_path, monkeypatch):
    monkeypatch.setattr(model_registry, "MODELS_DIR", tmp_path)
    for filename in model_registry.MODELS.values():
        (tmp_path / filename).touch()
    return ModelManager(FakeEngine(), Database(tmp_path / "test.db"))

def test_switch(manager):
    assert manager.switch("4b") == "Active model: 4b"
    assert manager.engine.is_loaded()

def test_recovery(manager):
    manager.engine.fail = "4b"
    assert "restored 1.7b" in manager.switch("4b")
    assert manager.engine.is_loaded()

def test_default(manager):
    assert manager.default() == "1.7b"
    manager.set_default("4b")
    assert ModelManager(FakeEngine(), manager.database).default() == "4b"
    assert manager.engine.model_id == "1.7b"

def test_invalid(manager):
    with pytest.raises(ValueError): manager.switch("../other")

def test_missing(manager):
    model_registry.model_path("4b").unlink()
    with pytest.raises(ValueError): manager.switch("4b")
    assert manager.engine.is_loaded()

def test_startup_fallback(manager):
    manager.set_default("4b")
    manager.engine.close()
    manager.engine.fail = "4b"
    assert "fallback" in manager.initialize()
    assert manager.engine.model_id == "1.7b"

def test_commands(manager):
    assert "installed" in manager.route("/models")
    assert manager.route("hello") is None
    assert "Invalid" in manager.route("/model-use")
