#!/usr/bin/env python3
"""PostToolUse hook: warn when hedge words are added to rule-like files
(CLAUDE.md, SKILL.md, hook scripts, command files). Non-blocking: exits 2 +
stderr so Claude reads the warning as feedback after the edit lands.
"""
import sys, json, re

try:
    payload = json.load(sys.stdin)
except Exception as e:
    print(f"hedge-scan: failed to parse input: {e}", file=sys.stderr)
    sys.exit(0)
if not isinstance(payload, dict):
    sys.exit(0)

tool_name = payload.get("tool_name", "")
if tool_name not in ("Edit", "Write", "MultiEdit"):
    sys.exit(0)

tool_input = payload.get("tool_input", {}) or {}
file_path = tool_input.get("file_path", "") or ""
if not file_path:
    sys.exit(0)

rule_patterns = [r"CLAUDE\.md$", r"SKILL\.md$", r"/hooks/.*\.(sh|py|md)$",
                 r"code-review-checklist\.md$", r"/commands/.*\.md$"]
if not any(re.search(p, file_path) for p in rule_patterns):
    sys.exit(0)

if tool_name == "Edit":
    added = tool_input.get("new_string", "") or ""
elif tool_name == "Write":
    added = tool_input.get("content", "") or ""
else:
    edits = tool_input.get("edits", []) or []
    added = "\n".join((e.get("new_string", "") or "") for e in edits if isinstance(e, dict))

added = re.sub(r"```[\s\S]*?```", "", added)

hedge_re = re.compile(
    r"\b(consider|try to|prefer|should probably|if possible|"
    r"when appropriate|might want to|usually|often|tends to|in general)\b",
    re.IGNORECASE,
)
list_or_rule_re = re.compile(r"^(\s*([-*]|\d+\.)\s|\s*\*\*)")

hits = []
quoted_re = re.compile(r"'[^']*'|\"[^\"]*\"|`[^`]*`")
for line in added.split("\n"):
    if not list_or_rule_re.match(line):
        continue
    # Strip quoted spans so quoted examples of hedge words do not false-positive
    candidate = quoted_re.sub("", line)
    m = hedge_re.search(candidate)
    if m:
        hits.append((line.strip(), m.group(0)))

if not hits:
    sys.exit(0)

msg = [f"Hedge word detected in added rule line(s) in {file_path}.",
       "Rules must use imperative language ('never', 'always', or a specific trigger condition)."]
for line, token in hits[:5]:
    msg.append(f"  - '{token}' in: {line[:140]}")
if len(hits) > 5:
    msg.append(f"  ... and {len(hits) - 5} more.")
print("\n".join(msg), file=sys.stderr)
sys.exit(2)
