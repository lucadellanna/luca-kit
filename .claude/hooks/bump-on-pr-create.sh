#!/bin/bash
# PreToolUse hook: bump plugin versions before any `gh pr create` call.
# Reads the Bash tool input JSON from stdin; exits 0 immediately for all
# other Bash commands so there is no overhead on normal tool calls.
set -euo pipefail

INPUT=$(cat)
COMMAND=$(python3 -c "import sys, json; d=json.load(sys.stdin); print(d.get('tool_input', {}).get('command', ''))" <<< "$INPUT" || true)

if [[ "$COMMAND" != *"gh pr create"* ]]; then
  exit 0
fi

REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null) || exit 0
cd "$REPO_ROOT"
python3 scripts/prepare-pr.py
git remote get-url origin >/dev/null 2>&1 || { echo "No 'origin' remote; skipping push." >&2; exit 0; }
BRANCH=$(git rev-parse --abbrev-ref HEAD)
git push -u origin "$BRANCH"
