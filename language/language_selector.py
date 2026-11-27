from language.language_preferences import SUPPORTED


class LanguageSelector:
    def __init__(self):
        self.last = "en"

    def reset(self):
        self.last = "en"

    def select(self, preference, detected):
        if preference in SUPPORTED[1:]:
            return preference
        code = {"mixed-hi": "hi", "mixed-bn": "bn"}.get(detected, detected)
        if code in SUPPORTED[1:]:
            self.last = code
            return code
        if code == "neutral":
            return self.last
        return "en"
