import json
from config import OUTPUTS_DIR
from intelligence.benchmark_engine import BenchmarkEngine

BENCHMARK_COMMANDS = {
    '/benchmark-help':'Show benchmark commands', '/benchmark-info':'Explain evaluation scope',
    '/benchmark-list':'List suites', '/benchmark-run components|model':'Run isolated suite',
    '/benchmark-results':'Show latest results', '/benchmark-history':'Show session runs',
    '/benchmark-compare':'Compare last two runs of same suite', '/benchmark-export':'Export latest JSON report',
}


def summary(run):
    rows = run['rows']
    counts = ', '.join(f'{s}: {sum(r["status"] == s for r in rows)}' for s in ('pass','fail','manual_review','error'))
    return f"{run['suite']} | {run['model']} | {counts} | {sum(r['seconds'] for r in rows):.2f}s"


class BenchmarkRouter:
    def __init__(self, model, output_dir=OUTPUTS_DIR):
        self.engine = BenchmarkEngine(model)
        self.output_dir = output_dir
        self.runs = []

    def route(self, message):
        parts = message.strip().lower().split()
        if not parts or not parts[0].startswith('/benchmark-'): return None
        cmd = parts[0]
        if cmd == '/benchmark-run' and len(parts)==2 and parts[1] in ('components','model'):
            run = self.engine.run(parts[1]); self.runs = (self.runs + [run])[-20:]
            return summary(run) + '\nUse /benchmark-results for details.'
        if len(parts)!=1: return 'See /benchmark-help.'
        if cmd == '/benchmark-help': return '\n'.join(f'{k}: {v}' for k,v in BENCHMARK_COMMANDS.items())
        if cmd == '/benchmark-info': return 'Component checks use fixed expectations. Raw model answers require manual review. No conversation, tools or memory writes. History: last 20 runs in this process.'
        if cmd == '/benchmark-list': return 'components: deterministic checks\nmodel: raw English factual and programming prompts (manual review)'
        if cmd not in ('/benchmark-results','/benchmark-history','/benchmark-compare','/benchmark-export'): return 'See /benchmark-help.'
        if not self.runs: return 'No benchmark runs yet.'
        run = self.runs[-1]
        if cmd == '/benchmark-history': return '\n'.join(summary(r) for r in self.runs)
        if cmd == '/benchmark-results': return summary(run)+'\n'+json.dumps(run['rows'],ensure_ascii=True,indent=2)
        if cmd == '/benchmark-compare':
            previous = next((r for r in reversed(self.runs[:-1]) if r['suite']==run['suite']),None)
            if previous is None: return 'Run the same suite twice first.'
            return 'Previous: '+summary(previous)+'\nLatest: '+summary(run)+'\nLatency varies; manual-review counts are not accuracy scores.'
        self.output_dir.mkdir(parents=True,exist_ok=True)
        path = self.output_dir / f"KlubAI_benchmark_{run['id']}.json"
        with path.open('x',encoding='utf8') as f: json.dump(run,f,ensure_ascii=True,indent=2)
        return f'Benchmark exported: {path}'
