from core.model_registry import MODELS, DEFAULT_MODEL, model_path

MODEL_COMMANDS = {
    "/models": "List supported local models",
    "/model-use ID": "Switch active model",
    "/model-info ID": "Show model file information",
    "/model-default [ID]": "Show or save startup model",
    "/model-help": "Show model commands",
}

class ModelManager:
    def __init__(self, engine, database):
        self.engine = engine
        self.database = database

    def default(self):
        with self.database.connect() as db:
            row = db.execute("SELECT value FROM application_settings WHERE key=?", ("default_model",)).fetchone()
        return row[0] if row and row[0] in MODELS else DEFAULT_MODEL

    def set_default(self, code):
        if not model_path(code).is_file():
            raise ValueError("Model file not installed.")
        with self.database.connect() as db:
            db.execute("INSERT INTO application_settings(key,value) VALUES (?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value, updated_at=CURRENT_TIMESTAMP", ("default_model", code))

    def switch(self, code):
        if not model_path(code).is_file():
            raise ValueError("Model file not installed.")
        old = self.engine.model_id
        if old == code and self.engine.is_loaded():
            return f"Active model: {code} (already loaded)"
        self.engine.close()
        self.engine.model_id = code
        try:
            self.engine.load_model()
        except (Exception, KeyboardInterrupt) as error:
            self.engine.close()
            self.engine.model_id = old
            try:
                self.engine.load_model()
            except Exception as recovery:
                raise RuntimeError("Model switch and recovery failed. Restart KlubAI.") from recovery
            if isinstance(error, KeyboardInterrupt):
                raise
            return f"Switch failed ({type(error).__name__}); restored {old}."
        return f"Active model: {code}"

    def initialize(self):
        code = self.default()
        try:
            self.engine.model_id = code
            self.engine.load_model()
        except Exception:
            if code == DEFAULT_MODEL:
                raise
            self.engine.close()
            self.engine.model_id = DEFAULT_MODEL
            self.engine.load_model()
            return "Saved model unavailable; loaded 1.7b fallback."
        return f"Active model: {code}"

    def route(self, message):
        parts = message.lower().split()
        if not parts:
            return None
        cmd, args = parts[0], parts[1:]
        if cmd == "/model-help" and not args:
            return "\n".join(f"{k}: {v}" for k,v in MODEL_COMMANDS.items())
        if cmd == "/models" and not args:
            return "\n".join(f"{k}: {v} | {'installed' if model_path(k).is_file() else 'missing'} | {'active' if self.engine.model_id == k and self.engine.is_loaded() else 'inactive'}" for k,v in MODELS.items())
        if cmd == "/model-default" and not args:
            return f"Startup model: {self.default()}"
        if cmd in ("/model-use", "/model-info", "/model-default") and len(args)==1:
            code = args[0]
            path = model_path(code)
            if cmd == "/model-use":
                return self.switch(code)
            if cmd == "/model-default":
                self.set_default(code)
                return f"Startup model saved: {code} (applies next launch)"
            return f"Model: {code}\nFile: {path.name}\nSize: {path.stat().st_size if path.is_file() else 0} bytes\nInstalled: {path.is_file()}"
        if cmd.startswith("/model-") or cmd == "/models":
            return "Invalid model command. Use /model-help."
        return None
