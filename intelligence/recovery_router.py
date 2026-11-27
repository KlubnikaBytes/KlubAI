from intelligence.response_recovery import ResponseRecovery

RECOVERY_COMMANDS = {
    '/recovery-help': 'Show recovery commands',
    '/recovery-info': 'Show recovery configuration',
    '/recovery-preview question | answer': 'Inspect recovery triggers without inference',
    '/recovery-last': 'Show last recovery decision',
    '/recovery-stats': 'Show session recovery totals',
    '/recovery-on': 'Enable recovery',
    '/recovery-off': 'Disable recovery',
}


class RecoveryRouter:
    def __init__(self, assistant):
        self.assistant = assistant
        self.engine = ResponseRecovery(assistant.quality_router.engine, assistant.verification_router.engine, assistant.fact_router.engine)
        self.enabled = True
        self.reset()

    def reset(self):
        self.last = None
        self.counts = dict(unchanged=0, curated=0, regenerated=0, fallback=0)

    def record(self, result):
        self.counts[result.outcome] += 1
        self.last = (result.outcome, result.reasons)

    def route(self, message):
        parts = message.strip().split(maxsplit=1)
        if not parts or not parts[0].lower().startswith('/recovery-'):
            return None
        cmd = parts[0].lower()
        if cmd == '/recovery-preview' and len(parts)==2 and '|' in parts[1]:
            q,a = parts[1].split('|',1)
            try:
                reasons = self.engine.reasons(q.strip(), a.strip(), self.assistant.quality_router.enabled, self.assistant.verification_router.enabled)
                return 'Recovery triggers: ' + ('; '.join(reasons) or 'None') + '\nPreview only; no inference or commands executed.'
            except ValueError as error:
                return str(error)
        if len(parts)==1:
            if cmd == '/recovery-help':
                return '\n'.join(f'{k}: {v}' for k,v in RECOVERY_COMMANDS.items())
            if cmd == '/recovery-info':
                return f'Recovery: {"enabled" if self.enabled else "disabled"}\nEnglish general model chat; respects quality, verification and fact toggles. At most one extra model call. No general factual guarantee.'
            if cmd == '/recovery-stats':
                return '\n'.join(f'{k.title()}: {v}' for k,v in self.counts.items())
            if cmd == '/recovery-last':
                return f'Outcome: {self.last[0]}\nTriggers: {"; ".join(self.last[1]) or "None"}' if self.last else 'No recovery assessment yet.'
            if cmd in ('/recovery-on','/recovery-off'):
                self.enabled = cmd == '/recovery-on'
                return f'Recovery: {"enabled" if self.enabled else "disabled"}'
        return 'Invalid recovery command. Use /recovery-help.'
