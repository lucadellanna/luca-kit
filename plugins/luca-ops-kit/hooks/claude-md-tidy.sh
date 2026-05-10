#!/bin/bash
# PostToolUse hook: CLAUDE.md tidiness gate
# Fires after Edit/Write/MultiEdit. Exits silently unless the target is a CLAUDE.md or AGENTS.md.
# When triggered, runs quantitative checks and injects review criteria.

set -euo pipefail

input=$(cat)

# Extract fields using python3 (available on macOS; no jq dependency)
eval "$(python3 -c "
import sys, json, shlex
try:
    d = json.load(sys.stdin)
    ti = d.get('tool_input') or {}
    fp = ti.get('file_path') or ''
    tn = d.get('tool_name') or ''
    edits = ti.get('edits') or []
    if edits:
        ns = ''.join((e.get('new_string') or '') for e in edits if isinstance(e, dict))
    else:
        ns = ti.get('new_string') or ''
    print(f'file_path={shlex.quote(fp)}')
    print(f'tool_name={shlex.quote(tn)}')
    print(f'new_string_len={len(ns)}')
except Exception:
    print('file_path=\"\"')
    print('tool_name=\"\"')
    print('new_string_len=0')
" <<< "$input" 2>/dev/null)" || exit 0

[[ -z "$file_path" ]] && exit 0

basename=$(basename -- "$file_path")

case "$basename" in
  CLAUDE.md|AGENTS.md) ;;
  *) exit 0 ;;
esac

[[ ! -f "$file_path" ]] && exit 0

# --- Quantitative metrics ---
line_count=$(wc -l < "$file_path" | tr -d ' ')
word_count=$(wc -w < "$file_path" | tr -d ' ')
heading_count=$(grep -c '^#' "$file_path" || true)
heading_count=${heading_count:-0}

max_para_lines=$(awk '
  /^[[:space:]]*$/ || /^#/ { if (count > max) max = count; count = 0; next }
  { count++ }
  END { if (count > max) max = count; print max+0 }
' "$file_path")

hedging=$(grep -ciE '\b(try to|consider|prefer|might want to|you could|if possible)\b' "$file_path" || true)
hedging=${hedging:-0}

long_bullets=$(awk '/^[[:space:]]*[-*] / && length > 120 { count++ } END { print count+0 }' "$file_path")

duplicate_lines=$({ grep -v '^[[:space:]]*$' "$file_path" || true; } | { grep -v '^[[:space:]]*#' || true; } | sed 's/^[[:space:]]*//; s/[[:space:]]*$//' | sort | uniq -d | wc -l | tr -d ' ')

# --- Diff context ---
if [[ "$tool_name" == "Edit" || "$tool_name" == "MultiEdit" ]]; then
  diff_summary="${tool_name}: new content is ${new_string_len} chars"
else
  diff_summary="Write: full file rewrite (${line_count} lines)"
fi

# --- Output review prompt ---
cat <<EOF
CLAUDE.md Tidiness Review ($basename, ${line_count} lines total, ${word_count} words):
${diff_summary}
File metrics: sections=$heading_count | longest-paragraph=${max_para_lines}-lines | hedging=$hedging | bullets>120ch=$long_bullets | duplicates=$duplicate_lines

Review the DIFF you just wrote against the existing file. If ANY criterion fails, revise now:

1. CONCISENESS: Can the new content lose words without losing signal? One sentence per rule. Tables over prose.
2. DUPLICATION: Does the new content repeat something already in this file or a parent/child CLAUDE.md?
3. CONTRADICTIONS: Does it conflict with an existing rule in this file or a related file?
4. BELONGS ELSEWHERE: Should this live in a skill, DESIGN.md, memory, or a script instead?
5. EPHEMERAL: Will this still be relevant in 30 days? If not, don't put it in CLAUDE.md.
6. VAGUE TRIGGERS: Does the new rule state WHEN it fires? "Consider..." is not a rule.
7. CONTEXT POLLUTION: Will this waste tokens in sessions where it's irrelevant? Narrow the scope.
EOF
