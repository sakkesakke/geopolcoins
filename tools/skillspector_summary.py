#!/usr/bin/env python3
"""Print one markdown table row (plus issue rows) for a SkillSpector JSON report. Used by .github/workflows/skill-scan.yml."""
import json, sys
name, path, code = sys.argv[1], sys.argv[2], sys.argv[3]
try:
    r = json.load(open(path))
except Exception as e:
    print(f"| {name} | could not read report ({type(e).__name__}) (exit {code}) |"); sys.exit(0)
a = r.get('risk_assessment') or {}
issues = r.get('issues') or []
sup = r.get('suppressed_count') or len(r.get('suppressed') or [])
print(f"| {name} | {a.get('recommendation','?')} · risk {a.get('score','?')} · {len(issues)} issue(s)" + (f" · {sup} reviewed and accepted" if sup else "") + f" (exit {code}) |")
for f in issues[:25]:
    loc = f.get('location') or {}
    text = str(f.get('title') or f.get('description') or f.get('message') or '')[:160].replace('|', '/').replace('\n', ' ')
    print(f"| ↳ {f.get('severity')} {f.get('id')} {f.get('category')} | {loc.get('file')}:{loc.get('start_line')} {text} |")
