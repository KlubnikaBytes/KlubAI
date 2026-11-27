"""Session-only quality metrics; no stored question or answer text."""
from intelligence.response_quality import ResponseQuality

QUALITY_COMMANDS = {
    '/quality-help':'Show quality commands',
    '/quality-info':'Show quality assessment configuration',
    '/quality-last':'Show last automatic assessment',
    '/quality-check question | answer':'Assess text without inference',
    '/quality-stats':'Show automatic assessment statistics',
    '/quality-on':'Enable automatic assessment',
    '/quality-off':'Disable automatic assessment',
}


class QualityRouter:
    def __init__(self):
        self.engine = ResponseQuality()
        self.enabled = True
        self.reset()

    def reset(self):
        self.last = None
        self.count = self.total = self.flagged = 0

    def record(self, question, answer):
        if not self.enabled:
            return
        report = self.engine.assess(question,answer)
        self.last = report
        self.count += 1
        self.total += report.score
        self.flagged += bool(report.issues)

    def route(self, message):
        parts = message.strip().split(maxsplit=1)
        if not parts:
            return None
        cmd = parts[0].lower()
        if cmd == '/quality-check' and len(parts)==2 and '|' in parts[1]:
            q,a = parts[1].split('|',1)
            try:
                return self.engine.assess(q,a).render()
            except ValueError as error:
                return str(error)
        if len(parts)==1:
            if cmd == '/quality-help':
                return '\n'.join(f'{k}: {v}' for k,v in QUALITY_COMMANDS.items())
            if cmd == '/quality-info':
                return f'Quality assessment: {"enabled" if self.enabled else "disabled"}\nEnglish general chat only; observation mode; no factual verification. Metrics reset on new conversation or data deletion.'
            if cmd == '/quality-last':
                return self.last.render() if self.last else 'No automatic assessment yet.'
            if cmd == '/quality-stats':
                average = self.total/self.count if self.count else 0
                return f'Assessed responses: {self.count}\nAverage score: {average:.2f}/100\nResponses with issues: {self.flagged}'
            if cmd in ('/quality-on','/quality-off'):
                self.enabled = cmd == '/quality-on'
                return f'Quality assessment: {"enabled" if self.enabled else "disabled"}'
        if cmd.startswith('/quality-'):
            return 'Invalid quality command. Use /quality-help.'
        return None
