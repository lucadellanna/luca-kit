import datetime
import json
import os
import subprocess
import sys


def run(cmd):
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.stdout.strip()
    except OSError:
        return ""


def warn(msg):
    print(f"reflect-log: {msg}", file=sys.stderr)


if not os.path.exists(os.path.expanduser("~/.claude/reflect-logs/.enabled")):
    sys.exit(0)

try:
    data = json.loads(sys.stdin.read())
except json.JSONDecodeError:
    sys.exit(0)

today = str(datetime.date.today())
if isinstance(data, dict):
    entry = {"schema": 3, "date": data.get("date") or today}
    for k in ("applied", "asked_accepted", "asked_rejected", "hints"):
        val = data.get(k, [])
        if not isinstance(val, list):
            val = []
        entry[k] = val
    # Coerce hint dicts to their recommendation string; warn on unexpected shape.
    coerced = []
    for h in entry["hints"]:
        if isinstance(h, str):
            coerced.append(h)
        elif isinstance(h, dict) and "recommendation" in h:
            coerced.append(h["recommendation"])
        else:
            warn(f"skipping malformed hint entry: {h!r}")
    entry["hints"] = coerced
    if not any(entry[k] for k in ("applied", "asked_accepted", "asked_rejected", "hints")):
        warn("schema 3 payload has no findings; nothing to log")
        sys.exit(0)
elif isinstance(data, list):
    entry = {"schema": 2, "date": today, "findings": data}
else:
    sys.exit(0)

origin = run(['git', 'remote', 'get-url', 'origin'])
if origin:
    clean = origin.rstrip('/')
    clean = clean[:-4] if clean.endswith('.git') else clean
    slug = '__'.join(clean.replace(':', '/').split('/')[-2:])
else:
    top = run(['git', 'rev-parse', '--show-toplevel'])
    slug = os.path.basename(top) or 'no-repo' if top else 'no-repo'
# ASCII-only to match the Bash sed 's/[^A-Za-z0-9_-]/-/g' in dream SKILL.md.
slug = ''.join(c if (c.isascii() and c.isalnum()) or c in '-_' else '-' for c in slug)

path = os.path.expanduser(f"~/.claude/reflect-logs/{slug}.jsonl")
try:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'a', encoding='utf-8') as f:
        try:
            f.write(json.dumps(entry) + '\n')
        except (TypeError, ValueError) as e:
            warn(f"failed to serialize entry: {e}")
            sys.exit(1)
except OSError as e:
    warn(f"failed to write {path}: {e}")
    sys.exit(1)
