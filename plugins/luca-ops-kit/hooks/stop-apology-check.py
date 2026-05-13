#!/usr/bin/env python3
"""Stop hook: block stop if a self-correction phrase appears in the last
assistant message with no rule-update widget, no rule-file edit, no error-log
append, and no explicit one-off escape. Self-contained: requires no external
config file to operate.
"""
import sys, json, re, os

try:
    payload = json.load(sys.stdin)
except Exception as e:
    print(f"stop-apology-check: failed to parse input: {e}", file=sys.stderr)
    sys.exit(0)
if not isinstance(payload, dict):
    sys.exit(0)

transcript_path = payload.get("transcript_path", "")
if not transcript_path or not os.path.isfile(transcript_path):
    sys.exit(0)

last_text = ""
last_tool_uses = []
with open(transcript_path, encoding="utf-8") as f:
    for line in f:
        try:
            entry = json.loads(line)
        except Exception:
            continue
        if not isinstance(entry, dict) or entry.get("type") != "assistant":
            continue
        msg = entry.get("message", {}) or {}
        content = msg.get("content", [])
        if not isinstance(content, list):
            continue
        parts = []
        tool_uses = []
        for c in content:
            if not isinstance(c, dict):
                continue
            if c.get("type") == "text":
                parts.append(c.get("text", "") or "")
            elif c.get("type") == "tool_use":
                tool_uses.append({"name": c.get("name", ""), "input": c.get("input", {}) or {}})
        last_text = "\n".join(parts)
        last_tool_uses = tool_uses

cleaned = re.sub(r"```[\s\S]*?```", "", last_text)
cleaned = "\n".join(l for l in cleaned.split("\n") if not l.lstrip().startswith(">"))

apology_re = re.compile(
    r"\b(you'?re right|good catch|my mistake|i shouldn'?t have|"
    r"i should have|i missed|i apologi[sz]e|the issue was)\b",
    re.IGNORECASE,
)
if not apology_re.search(cleaned):
    sys.exit(0)

escape_phrases = ("genuinely unpredictable", "no class applies", "one-off", "single typo")
has_escape = any(p in cleaned.lower() for p in escape_phrases)
has_widget = bool(re.search(r"`★\s*rule-update\s*─+`", last_text))

rule_patterns = [r"CLAUDE\.md$", r"SKILL\.md$", r"/hooks/.*\.(sh|py|md)$",
                 r"code-review-checklist\.md$", r"/commands/.*\.md$"]
error_log_re = re.compile(r"error-log\.md")

write_op_re = re.compile(r"(>>|\btee\b|(?<![>])>(?![>]))")

has_rule_edit = False
has_log_append = False
for tu in last_tool_uses:
    name = tu.get("name", "")
    inp = tu.get("input", {}) or {}
    cmd = inp.get("command", "") or ""
    if name in ("Edit", "Write"):
        # Use `or` chain without default="" so an explicit null value doesn't mask the fallback
        fp_raw = inp.get("file_path") or inp.get("notebook_path")
        fp = fp_raw if isinstance(fp_raw, str) else ""
        if fp:
            if any(re.search(p, fp) for p in rule_patterns):
                has_rule_edit = True
            if error_log_re.search(fp):
                has_log_append = True
    elif name == "MultiEdit":
        for edit in inp.get("edits", []) or []:
            if not isinstance(edit, dict):
                continue
            fp_raw = edit.get("file_path") or ""
            fp = fp_raw if isinstance(fp_raw, str) else ""
            if fp:
                if any(re.search(p, fp) for p in rule_patterns):
                    has_rule_edit = True
                if error_log_re.search(fp):
                    has_log_append = True
    elif name == "Bash":
        if error_log_re.search(cmd) and write_op_re.search(cmd):
            has_log_append = True
        if any(re.search(p, cmd) for p in rule_patterns) and (write_op_re.search(cmd) or bool(re.search(r"\bsed\s+-[^ ]*i", cmd))):
            has_rule_edit = True

has_structural_scope = bool(re.search(r"Scope:.*structural", last_text, re.IGNORECASE))

if has_escape or (has_widget and has_log_append and (has_rule_edit or has_structural_scope)):
    sys.exit(0)

reason = (
    "Self-correction phrase detected with no rule-update widget, rule-file edit, "
    "error-log append, or one-off escape. Before stopping, render this widget verbatim "
    "(backticks around the framing lines are required for machine detection):\n\n"
    "`★ rule-update ─────────────────────────────────`\n"
    "Error class: <name the class, not the instance>\n"
    "Rule: <imperative sentence preventing all instances>\n"
    "Scope: <file to edit, e.g. plugins/<name>/CLAUDE.md | skill <name> | hook <name> | structural (tool/code change needed)>\n"
    "Edit: <the Edit tool call follows in this same response; machine-enforced: the widget alone without an actual Edit tool call will not pass the Stop hook. If Scope = structural, propose the structural fix and ask before coding.>\n"
    "`─────────────────────────────────────────────────`\n\n"
    "Then append one line to ~/.claude/error-log.md: 'YYYY-MM-DD | <class> | <file>'. "
    "If genuinely a one-off (no class applies), say so explicitly. "
    "Full contract: plugins/luca-ops-kit/CLAUDE.md."
)
print(json.dumps({"decision": "block", "reason": reason}))
sys.exit(0)
