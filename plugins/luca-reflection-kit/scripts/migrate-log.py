"""Normalize reflect log entries across schemas 1, 2, 3.

Usage: migrate-log.py <log-path> [<since-date>]

Reads the JSONL log line by line, filters by date (>= since-date), and
emits a JSON array of normalized records to stdout. Each record has the
shape:

    {
        "date": "<YYYY-MM-DD>",
        "applied":         [ {"target": ..., "text": ...}, ... ],
        "asked_accepted":  [ {"target": ..., "text": ...}, ... ],
        "asked_rejected":  [ {"target": ..., "text": ...}, ... ],
        "hints":           [ "<recommendation>", ... ],
        "historical":      [ "<finding text>", ... ]
    }

Schema 1 (typed-findings objects) and schema 2 (plain-string findings)
have no acceptance-state information; their findings land in `historical`.
Schema 3 fills the acceptance buckets natively. Unknown schemas are
silently skipped.
"""

import json
import sys


def normalize(entry):
    rec = {
        "date": entry.get("date") or "1970-01-01",
        "applied": [],
        "asked_accepted": [],
        "asked_rejected": [],
        "hints": [],
        "historical": [],
    }
    schema = entry.get("schema", 0)
    if schema == 3:
        rec["applied"] = [e for e in (entry.get("applied") or []) if isinstance(e, dict)]
        rec["asked_accepted"] = [e for e in (entry.get("asked_accepted") or []) if isinstance(e, dict)]
        rec["asked_rejected"] = [e for e in (entry.get("asked_rejected") or []) if isinstance(e, dict)]
        rec["hints"] = [h if isinstance(h, str) else str(h) for h in (entry.get("hints") or [])]
        return rec
    if schema == 2:
        rec["historical"] = entry.get("findings") or []
        return rec
    if schema == 1:
        for f in entry.get("findings") or []:
            if isinstance(f, dict):
                text = f.get("text") or str(f)
                target = f.get("target") or f.get("memory_target") or f.get("skill")
                rec["historical"].append(f"{target}: {text}" if target else text)
            else:
                rec["historical"].append(str(f))
        return rec
    return None


def main():
    if len(sys.argv) < 2:
        print("[]")
        return
    path = sys.argv[1]
    since = sys.argv[2] if len(sys.argv) > 2 else "1970-01-01"
    out = []
    try:
        f = open(path, encoding="utf-8")
    except OSError:
        print("[]")
        return
    with f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue
            if not isinstance(entry, dict):
                continue
            if (entry.get("date") or "1970-01-01") < since:
                continue
            rec = normalize(entry)
            if rec is not None:
                out.append(rec)
    print(json.dumps(out))


if __name__ == "__main__":
    main()
