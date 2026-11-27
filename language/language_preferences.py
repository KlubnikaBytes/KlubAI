SUPPORTED = ("auto", "en", "hi", "bn", "hinglish")


class LanguagePreferences:
    def __init__(self, database):
        self.database = database

    def get(self):
        with self.database.connect() as db:
            row = db.execute("SELECT value FROM application_settings WHERE key = ?", ("language_preference",)).fetchone()
        return row[0] if row and row[0] in SUPPORTED else "auto"

    def set(self, code):
        if code not in SUPPORTED:
            raise ValueError("Unsupported preference. Use auto, en, hi, bn or hinglish.")
        with self.database.connect() as db:
            db.execute("INSERT INTO application_settings(key,value) VALUES (?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value, updated_at=CURRENT_TIMESTAMP", ("language_preference", code))

    def reset(self):
        with self.database.connect() as db:
            db.execute("DELETE FROM application_settings WHERE key = ?", ("language_preference",))
