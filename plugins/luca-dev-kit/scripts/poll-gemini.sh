#!/bin/bash
# Poll for a new Gemini review on the current PR.
# Usage: poll-gemini.sh <pr_number> <trigger_iso_timestamp>
# Exit 0 + prints JSON review object: new review found since trigger_ts
# Exit 1: no new review yet
# Exit 2: usage error, tool failure, or parse error

set -euo pipefail

PR_NUM="${1:-}"
TRIGGER_TS="${2:-}"

if [[ -z "$PR_NUM" || -z "$TRIGGER_TS" ]]; then
  echo "Usage: poll-gemini.sh <pr_number> <trigger_iso_timestamp>" >&2
  exit 2
fi

REVIEW=$(gh pr view "$PR_NUM" --json reviews -q '
  .reviews
  | map(select(.author.login == "gemini-code-assist"))
  | last
  | select(. != null)
' 2>/dev/null) || { echo "Failed to fetch PR reviews" >&2; exit 2; }

if [[ -z "$REVIEW" ]]; then
  exit 1
fi

REVIEW_TS=$(echo "$REVIEW" | python3 -c "import sys,json; print(json.load(sys.stdin)['submittedAt'])") || { echo "Failed to parse review timestamp" >&2; exit 2; }

# Compare timestamps: normalize both to UTC seconds for robust comparison.
IS_NEW=$(TRIGGER_TS="$TRIGGER_TS" REVIEW_TS="$REVIEW_TS" python3 -c "
from datetime import datetime, timezone
import sys, os

def to_utc(s):
    # Handle both 'Z' suffix and '+00:00' offset forms
    s = s.strip()
    if s.endswith('Z'):
        s = s[:-1] + '+00:00'
    return datetime.fromisoformat(s).astimezone(timezone.utc)

try:
    trigger = to_utc(os.environ['TRIGGER_TS'])
    review  = to_utc(os.environ['REVIEW_TS'])
    print('1' if review > trigger else '')
except Exception as e:
    print(f'Error comparing timestamps: {e}', file=sys.stderr)
    sys.exit(2)
")

if [[ -n "$IS_NEW" ]]; then
  echo "$REVIEW"
  exit 0
fi

exit 1
