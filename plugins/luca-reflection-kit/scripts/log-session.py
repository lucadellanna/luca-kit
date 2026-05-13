import json, os, sys, datetime, subprocess

def run(cmd):
    try: return subprocess.run(cmd, capture_output=True, text=True).stdout.strip()
    except OSError: return ""

if not os.path.exists(os.path.expanduser("~/.claude/reflect-logs/.enabled")):
    sys.exit(0)

try:
    findings = json.loads(sys.stdin.read())
except json.JSONDecodeError:
    sys.exit(0)
if not isinstance(findings, list):
    sys.exit(0)

origin = run(['git', 'remote', 'get-url', 'origin'])
if origin:
    clean = origin.rstrip('/')
    clean = clean[:-4] if clean.endswith('.git') else clean
    slug = '__'.join(clean.replace(':', '/').split('/')[-2:])
else:
    top = run(['git', 'rev-parse', '--show-toplevel'])
    slug = os.path.basename(top) or 'no-repo' if top else 'no-repo'
slug = ''.join(c if c.isalnum() or c in '-_' else '-' for c in slug)

path = os.path.expanduser(f"~/.claude/reflect-logs/{slug}.jsonl")
os.makedirs(os.path.dirname(path), exist_ok=True)
entry = {
    "schema": 2,
    "date": str(datetime.date.today()),
    "findings": findings,
}
with open(path, 'a', encoding='utf-8') as f:
    f.write(json.dumps(entry) + '\n')
