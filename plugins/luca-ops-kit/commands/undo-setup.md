---
description: Removes CLAUDE.md rules added by /luca-ops-recommended-setup. Run this before uninstalling luca-ops-kit.
---

# Undo Setup

You reverse the changes made by `/luca-ops-recommended-setup`. Run this before uninstalling luca-ops-kit. Speak in plain language.

## Step 1: Detect what to remove

Read `~/.claude/CLAUDE.md`. Search for lines containing any of these fingerprints:

| Rule | Fingerprint |
|------|-------------|
| Use skills first | `<!-- luca-ops-kit:rule-skills-first -->` |
| Confirm irreversible | `<!-- luca-ops-kit:rule-confirm-irreversible -->` |
| Clarifying question | `<!-- luca-ops-kit:rule-clarifying-question -->` |

- If `~/.claude/CLAUDE.md` does not exist: tell the user "No CLAUDE.md found; nothing to undo." and stop.
- If no fingerprints are found: tell the user "No luca-ops-kit rules found in your CLAUDE.md. Nothing to undo." Clean up the marker (Step 4) and stop.

## Step 2: Show what will be removed

Display each fingerprinted line that was found. Use AskUserQuestion (open text):
> "These rules will be removed from your CLAUDE.md. Type 'yes' to confirm, or 'cancel' to stop."

Only proceed on explicit "yes" (case-insensitive). Any other response: stop without making changes.

## Step 3: Remove rules from CLAUDE.md

Execute the following Python block via Bash:

```python
import os

fingerprints = [
    "<!-- luca-ops-kit:rule-skills-first -->",
    "<!-- luca-ops-kit:rule-confirm-irreversible -->",
    "<!-- luca-ops-kit:rule-clarifying-question -->",
]

path = os.path.expanduser("~/.claude/CLAUDE.md")
try:
    with open(path) as f:
        lines = f.readlines()
except FileNotFoundError:
    print("~/.claude/CLAUDE.md not found")
    raise SystemExit(0)

found = []
filtered = []
for line in lines:
    matched = next((fp for fp in fingerprints if fp in line), None)
    if matched:
        found.append(matched)
    else:
        filtered.append(line)

# Remove empty section header if no content follows it
HEADER = "## Suggested defaults (luca-ops-kit)"
result = []
i = 0
while i < len(filtered):
    if filtered[i].rstrip() == HEADER:
        j = i + 1
        while j < len(filtered) and filtered[j].strip() == "":
            j += 1
        if j >= len(filtered) or filtered[j].startswith("#"):
            i = j
            continue
    result.append(filtered[i])
    i += 1

tmp = path + ".tmp"
try:
    with open(tmp, "w") as tf:
        tf.writelines(result)
        tf.flush()
        os.fsync(tf.fileno())
    os.replace(tmp, path)
except OSError as e:
    print(f"FAILED: {e}")
    raise SystemExit(1)

for fp in found:
    rid = fp.replace("<!-- luca-ops-kit:", "").replace(" -->", "")
    print(f"Removed: {rid}")
for fp in fingerprints:
    if fp not in found:
        rid = fp.replace("<!-- luca-ops-kit:", "").replace(" -->", "")
        print(f"Already absent: {rid}")
```

If the script prints "FAILED": tell the user "The CLAUDE.md update failed. Check disk space and file permissions, then re-run /undo-setup." Stop.

## Step 4: Clean up marker

Use Bash:
```bash
rm -f ~/.claude/luca-ops-kit/setup-complete
rm -f ~/.claude/luca-ops-kit/applied.json
rmdir ~/.claude/luca-ops-kit 2>/dev/null || true
```

## Step 5: Summarize

Tell the user:
- Which rules were removed
- Which were already absent (if any)
- "You can now uninstall luca-ops-kit."

## Self-reflection

During execution, follow the self-observation protocol (see CLAUDE.md Principles).

Spawn a Haiku sub-agent to score this run (0-10 each), with instruction: "Score each criterion 0-10. For each, give a one-sentence rationale. Return a markdown table; no preamble.":

1. **Completeness**: every fingerprinted rule was found and removed, or its absence was correctly noted
2. **Safety**: nothing was deleted without explicit user confirmation; atomic write prevented CLAUDE.md corruption
3. **User communication**: the preview and summary are specific enough that the user knows exactly what changed

Average >= 9.5 -> stop. Otherwise revise and re-score (max 3 iterations; stop if score does not improve). Any criterion < 8 -> draft a concise edit to this file, show to user, apply on approval.
