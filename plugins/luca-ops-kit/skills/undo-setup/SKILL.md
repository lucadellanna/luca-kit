---
name: undo-setup
description: Removes all changes made by /luca-ops-recommended-setup (CLAUDE.md rules, hooks, hook scripts) so the plugin can be cleanly uninstalled. Run this before uninstalling luca-ops-kit.
version: 0.1.0
---

# Undo Setup

You reverse the changes made by `/luca-ops-recommended-setup`. Run this before uninstalling luca-ops-kit. Speak in plain language.

## Step 1: Read the manifest

Use Read to open `~/.claude/luca-ops-kit/applied.json`.

- If the file does not exist: tell the user "No setup manifest found at ~/.claude/luca-ops-kit/applied.json. Either /luca-ops-recommended-setup was never run, or the manifest was deleted. Nothing to undo." and stop.
- If the file exists: parse it. Use `rules_added` and `hooks_added` from the JSON; if either key is absent, treat it as an empty list and continue.

## Step 2: Show what will be removed

Present a clear summary before touching anything:

**Rules to remove from `~/.claude/CLAUDE.md`:**
- For each rule ID in `rules_added`, show the fingerprint (`<!-- luca-ops-kit:{rule-id} -->`)

**Hooks to remove from `~/.claude/settings.json` and disk:**
- For each hook ID in `hooks_added`, show the script filename and the settings.json command entry that references it

Use AskUserQuestion (open text):
> "This is everything that will be removed. Type 'yes' to confirm, or 'cancel' to stop."

Only proceed on explicit "yes" (case-insensitive). Any other response: stop without making changes.

## Step 3: Remove CLAUDE.md rules

Execute the following Python block via Bash. Substitute `rules_added_ids` with the `rules_added` list from Step 1 (a list of short IDs such as `["rule-skills-first", "rule-confirm-irreversible", "rule-clarifying-question"]`). The block reads CLAUDE.md directly and handles the not-found case internally -- no separate Bash existence check is needed:

```python
import os

# Derive fingerprints from rule IDs -- format is always <!-- luca-ops-kit:{rule-id} -->
to_remove = [f"<!-- luca-ops-kit:{rid} -->" for rid in rules_added_ids]

path = os.path.expanduser("~/.claude/CLAUDE.md")
try:
    with open(path) as f:
        lines = f.readlines()
except FileNotFoundError:
    print("~/.claude/CLAUDE.md not found -- skipping rule removal")
    raise SystemExit(0)
found = []
filtered = []
for line in lines:
    matched = next((fp for fp in to_remove if fp in line), None)
    if matched:
        found.append(matched)
    else:
        filtered.append(line)

# Remove empty section header: if the header line exists and no bullet
# lines follow it before the next heading or end of file, drop it.
HEADER = "## Suggested defaults (luca-ops-kit)"
result = []
i = 0
while i < len(filtered):
    if filtered[i].rstrip() == HEADER:
        # Look ahead: skip blank lines; if next non-blank is a bullet or content, keep header
        j = i + 1
        while j < len(filtered) and filtered[j].strip() == "":
            j += 1
        if j >= len(filtered) or filtered[j].startswith("#"):
            i = j  # skip header and trailing blanks
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
    print(f"Failed to write ~/.claude/CLAUDE.md: {e}. Rules may not have been removed.")
    raise SystemExit(1)

# Report absent fingerprints (extract human-readable ID from the HTML comment)
for fp in to_remove:
    if fp not in found:
        rule_id = fp.replace("<!-- luca-ops-kit:", "").replace(" -->", "")
        print(f"Rule already absent: {rule_id}")
```

Report any fingerprints not found: "Rule already absent: <id>" (e.g. `rule-skills-first`).

If a "Failed to write ~/.claude/CLAUDE.md" message is printed, tell the user: "The CLAUDE.md update failed. Check disk space and file permissions, then re-run /undo-setup." Stop without proceeding to Step 4.

## Step 4: Remove hooks from settings.json

For each hook ID in `hooks_added`, determine its script filename:

| Hook ID | Script filename |
|---------|----------------|
| `optimization-hint` | `optimization-hint.sh` |
| `prompt-word-count` | `prompt-word-count.sh` |

Execute the following Python block via Bash for each hook ID to remove its entry atomically:

```python
import json, os, fcntl

script_name = "<name>.sh"
path = os.path.expanduser("~/.claude/settings.json")
lock_path = path + ".lock"
try:
    with open(lock_path, "a") as lock_f:
        fcntl.flock(lock_f, fcntl.LOCK_EX)
        try:
            with open(path) as f:
                s = json.load(f)
        except FileNotFoundError:
            s = None  # settings.json already gone; nothing to remove
        except json.JSONDecodeError:
            print("~/.claude/settings.json contains invalid JSON -- cannot modify it safely. Inspect the file and try again.")
            raise SystemExit(1)
        if s is not None and isinstance(s, dict):
            hooks = s.get("hooks", {})
            if not isinstance(hooks, dict):
                hooks = {}
                s["hooks"] = hooks
            upsub = hooks.get("UserPromptSubmit", [])
            if not isinstance(upsub, list):
                upsub = []
            new_upsub = []
            changed = False
            for entry in upsub:
                if not isinstance(entry, dict):
                    new_upsub.append(entry)
                    continue
                hooks_list = entry.get("hooks", [])
                if not isinstance(hooks_list, list):
                    hooks_list = []
                remaining = [h for h in hooks_list if not (isinstance(h, dict) and h.get("command") == f"bash ~/.claude/hooks/{script_name}")]
                if len(remaining) != len(hooks_list):
                    changed = True
                    if remaining:
                        new_upsub.append({**entry, "hooks": remaining})
                    # else: entry has no hooks left; drop it entirely
                else:
                    new_upsub.append(entry)
            if changed:
                s["hooks"]["UserPromptSubmit"] = new_upsub
                tmp = path + ".tmp"
                try:
                    with open(tmp, "w") as tf:
                        json.dump(s, tf, indent=2)
                        tf.write('\n')
                        tf.flush()
                        os.fsync(tf.fileno())
                    os.replace(tmp, path)
                except OSError as e:
                    print(f"Failed to write ~/.claude/settings.json: {e}. The hook entry was not removed.")
                    raise SystemExit(1)
except PermissionError:
    print(f"Cannot write to {path} -- check permissions.")
    raise
```

If a PermissionError is raised, tell the user: "Cannot write to ~/.claude/settings.json; check file permissions. The hook entry was not removed." Stop without executing the remaining steps.

If a JSONDecodeError output is printed, tell the user: "~/.claude/settings.json contains invalid JSON and cannot be safely modified. Inspect the file manually and try again." Stop without executing the remaining steps.

If an OSError output is printed during the write phase, tell the user: "Failed to write to ~/.claude/settings.json. The hook entry was not removed." Stop without executing the remaining steps.

## Step 5: Remove or restore hook scripts

Hook ID to script filename mapping (same table as Step 4): `optimization-hint` → `optimization-hint.sh`, `prompt-word-count` → `prompt-word-count.sh`.

For each hook ID in `hooks_added`:

Check the manifest for a `hooks_backed_up` entry mapping the hook ID to a backup path (e.g., `~/.claude/hooks/<name>.sh.bak-luca-ops-kit`). This entry is written when `/luca-ops-recommended-setup` backed up a pre-existing file before overwriting.

- **If a backup path is recorded**: restore it. Use the absolute path stored in the manifest directly as the source (do not reconstruct it). Use Bash to run:
  ```bash
  mv "<absolute-backup-path-from-manifest>" ~/.claude/hooks/<name>.sh
  ```
  Note "Restored original: ~/.claude/hooks/<name>.sh"

- **If no backup**: delete the script. Use Bash to run:
  ```bash
  rm -f ~/.claude/hooks/<name>.sh
  ```
  If the file does not exist, note it and continue.

## Step 6: Delete manifest and marker

Use Bash to run:
```bash
rm -f ~/.claude/luca-ops-kit/applied.json
rm -f ~/.claude/luca-ops-kit/setup-complete
```

If `~/.claude/luca-ops-kit/` is now empty, remove the directory. Use Bash to run:
```bash
rmdir ~/.claude/luca-ops-kit 2>/dev/null || true
```

## Step 7: Summarize

Tell the user:
- What was removed (rules, hooks, scripts)
- What was not found and therefore skipped
- "You can now uninstall luca-ops-kit. Changes to ~/.claude/settings.json take effect next time Claude starts."

## Self-reflection

During execution, follow the self-observation protocol (see CLAUDE.md Principles).

Spawn a Haiku sub-agent to score this run (0–10 each), with instruction: "Score each criterion 0–10. For each, give a one-sentence rationale. Return a markdown table; no preamble.":

1. **Completeness**: every item in the manifest was found and removed, or its absence was correctly noted
2. **Safety**: nothing was deleted without explicit user confirmation; atomic writes prevented settings.json corruption
3. **Cleanliness**: no fingerprinted content remains in CLAUDE.md or settings.json after the run; marker and manifest are gone
4. **User communication**: the Step 2 preview and Step 7 summary are specific enough that the user knows exactly what changed and what to do next

Average ≥ 9.5 → stop. Otherwise revise and re-score (max 3 iterations; stop if score does not improve). Any criterion < 8 → draft a SKILL.md edit, show to user, apply on approval.

