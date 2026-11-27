from intelligence.question_classifier import QuestionClassifier

INTELLIGENCE_COMMANDS = {
    "/classify text": "Inspect question intent without executing it",
    "/intelligence-info": "Show classifier status",
    "/intelligence-help": "Show intelligence commands",
}


class IntelligenceRouter:
    def __init__(self):
        self.classifier = QuestionClassifier()

    def route(self, text):
        parts = text.strip().split(maxsplit=1)
        if not parts:
            return None
        cmd = parts[0].lower()
        if cmd == "/classify":
            if len(parts) != 2:
                return "Usage: /classify Your question"
            try:
                result = self.classifier.classify(parts[1])
            except ValueError as error:
                return str(error)
            return f"Intent: {result.intent}\nReason: {result.reason}\nMode: observation only"
        if cmd == "/intelligence-info" and len(parts) == 1:
            return "Question classifier: enabled\nMethod: local English rules\nMode: observation only; existing routing unchanged"
        if cmd == "/intelligence-help" and len(parts) == 1:
            return "\n".join(f"{k}: {v}" for k, v in INTELLIGENCE_COMMANDS.items())
        if cmd.startswith("/intelligence-"):
            return "Invalid intelligence command. Use /intelligence-help."
        return None
