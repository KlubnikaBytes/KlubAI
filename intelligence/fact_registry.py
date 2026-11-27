import json
import re
from config import DATASETS_DIR
from urllib.parse import urlsplit

class FactRegistry:
    def __init__(self, path=None):
        self.path = path or DATASETS_DIR / "trusted_facts.json"
        self.records = self.load()

    def load(self):
        rows = json.loads(self.path.read_text(encoding="utf-8"))
        if not isinstance(rows, list) or not rows or len(rows)>10000:
            raise ValueError("Invalid fact dataset")
        ids, keys = set(), set()
        for row in rows:
            if not isinstance(row, dict) or set(row) != {"id","entity","predicate","answer","publisher","url"}:
                raise ValueError("Invalid fact fields")
            if any(not isinstance(v,str) or not v.strip() or len(v)>2000 or any(ord(c)<32 for c in v) for v in row.values()):
                raise ValueError("Invalid fact value")
            key = (row["entity"].casefold(),row["predicate"])
            url = urlsplit(row["url"])
            if not re.fullmatch(r"[a-z0-9_]+",row["id"]) or row["predicate"] not in {"definition","creator"} or url.scheme!="https" or not url.hostname or url.username or url.password or row["id"] in ids or key in keys:
                raise ValueError("Invalid or duplicate fact")
            ids.add(row["id"]); keys.add(key)
        return rows
