from intelligence.answer_verifier import AnswerVerifier

VERIFY_COMMANDS = {
    '/verify-help': 'Show verification commands',
    '/verify-info': 'Show verification scope',
    '/verify-answer text': 'Assess supplied text locally',
    '/verify-last': 'Show last automatic assessment',
    '/verify-stats': 'Show automatic assessment totals',
    '/verify-on': 'Enable automatic assessment',
    '/verify-off': 'Disable automatic assessment',
}


class VerificationRouter:
    def __init__(self, registry=None):
        self.engine = AnswerVerifier(registry)
        self.enabled = True
        self.reset()

    def reset(self):
        self.last = None
        self.count = self.supported = self.contradicted = self.unverified = 0

    def record(self, answer):
        if not self.enabled:
            return
        report = self.engine.assess(answer)
        self.last = report
        self.count += 1
        self.supported += report.supported
        self.contradicted += report.contradicted
        self.unverified += report.unverified

    def route(self, message):
        parts = message.strip().split(maxsplit=1)
        if not parts:
            return None
        cmd = parts[0].lower()
        if cmd == '/verify-answer' and len(parts)==2:
            try:
                return self.engine.assess(parts[1]).render()
            except ValueError as error:
                return str(error)
        if len(parts)==1:
            if cmd == '/verify-help':
                return '\n'.join(f'{k}: {v}' for k,v in VERIFY_COMMANDS.items())
            if cmd == '/verify-info':
                return f'Verification: {"enabled" if self.enabled else "disabled"}\nEnglish general model chat; exact curated statements and explicit negations only. Observation mode; no answer changes. Session-only metrics.'
            if cmd == '/verify-last':
                return self.last.render() if self.last else 'No automatic verification yet.'
            if cmd == '/verify-stats':
                return f'Assessed responses: {self.count}\nSupported: {self.supported}\nContradicted: {self.contradicted}\nUnverified: {self.unverified}'
            if cmd in ('/verify-on','/verify-off'):
                self.enabled = cmd == '/verify-on'
                return f'Verification: {"enabled" if self.enabled else "disabled"}'
        if cmd.startswith('/verify-'):
            return 'Invalid verification command. Use /verify-help.'
        return None
