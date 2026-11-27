from intelligence.factual_knowledge import FactualKnowledge

FACT_COMMANDS = {
    "/fact-help":"Show factual commands", "/fact-info":"Show configuration", "/fact-stats":"Count facts", "/fact-list":"List entities", "/fact-search query":"Search records", "/fact-ask question":"Ask curated facts", "/fact-source ID":"Show reference", "/fact-verify":"Validate dataset structure", "/fact-on":"Enable automatic matching", "/fact-off":"Disable automatic matching",
}

class FactRouter:
    def __init__(self, engine=None):
        self.engine = engine or FactualKnowledge()
        self.enabled = True

    def route(self, message):
        parts = message.strip().split(maxsplit=1)
        if not parts or not parts[0].lower().startswith("/fact-"):
            return None
        cmd = parts[0].lower(); arg = parts[1].strip() if len(parts)>1 else ""
        rows = self.engine.registry.records
        if cmd in {"/fact-ask","/fact-search","/fact-source"}:
            if not arg or len(arg)>1000:
                return "Provide a valid argument (1-1000 characters)."
            if cmd == "/fact-ask":
                return self.engine.answer(arg) or "No matching curated fact."
            if cmd == "/fact-source":
                return next((self.engine.render(r) for r in rows if r['id']==arg.casefold()),"Fact not found.")
            return "\n".join(r['id']+": "+r['answer'] for r in rows if arg.casefold() in (r['entity']+' '+r['answer']+' '+r['id']).casefold()) or "No matching facts."
        if arg:
            return "Invalid fact command. Use /fact-help."
        if cmd == "/fact-help": return "\n".join(f"{k}: {v}" for k,v in FACT_COMMANDS.items())
        if cmd == "/fact-info": return f"Automatic matching: {'enabled' if self.enabled else 'disabled'}\nEnglish exact question patterns; curated references, not live verification."
        if cmd == "/fact-stats": return f"Facts: {len(rows)}\nEntities: {len({r['entity'] for r in rows})}"
        if cmd == "/fact-list": return "\n".join(sorted({r['entity'] for r in rows}))
        if cmd == "/fact-verify":
            try: self.engine.registry.load()
            except (ValueError,OSError): return "Dataset validation failed."
            return "Dataset structure valid. Source accuracy requires separate review."
        if cmd in {"/fact-on","/fact-off"}:
            self.enabled = cmd == "/fact-on"
            return "Automatic factual matching " + ("enabled" if self.enabled else "disabled")
        return "Invalid fact command. Use /fact-help."
