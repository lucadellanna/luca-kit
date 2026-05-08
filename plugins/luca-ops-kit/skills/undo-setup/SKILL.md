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
- For each rule ID in `rules_added`, show the fingerprint and the corresponding rule text

**Hooks to remove from `~/.claude/settings.json` and disk:**
- For each hook ID in `hooks_added`, show the script filename and the settings.json command entry that references it

Use AskUserQuestion (open text):
> "This is everything that will be removed. Type 'yes' to confirm, or 'cancel' to stop."

Only proceed on explicit "yes" (case-insensitive). Any other response: stop without making changes.

## Step 3: Remove CLAUDE.md rules

Execute the following Python block via Bash (substitute `rules_added` list from Step 1). The block reads CLAUDE.md directly and handles the not-found case internally -- no separate Bash existence check is needed:

```python
import os

fingerprints = ["<!-- luca-ops-kit:rule-skills-first -->",
                "<!-- luca-ops-kit:rule-confirm-irreversible -->",
                "<!-- luca-ops-kit:rule-clarifying-question -->"]
# Filter to only those in rules_added from Step 1
to_remove = [fp for fp in fingerprints if fp in rules_added_as_fingerprint_list]

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
with open(tmp, "w") as tf:
    tf.writelines(result)
    tf.flush()
    os.fsync(tf.fileno())
os.replace(tmp, path)

# Report absent fingerprints
for fp in to_remove:
    if fp not in found:
        print(f"Rule already absent: {fp}")
```

Report any fingerprints not found: "Rule already absent: <id>".

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
                remaining = [h for h in hooks_list if isinstance(h, dict) and script_name not in h.get("command", "")]
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

## Design decisions

| Decision | Rationale |
|----------|-----------|
| Manifest as source of truth (not re-scanning) | Re-scanning for fingerprints is fragile if the user edited CLAUDE.md; the manifest records exactly what was added |
| Dedicated lock file (`settings.json.lock`) for flock synchronization | Same reason as in luca-ops-recommended-setup: `fcntl.flock` locks an inode; after `os.replace()` new openers get the new inode with no lock; a persistent `.lock` file ensures synchronization across replacements |
| Hook removal filters within entries, not whole entries | A UserPromptSubmit entry can contain multiple hook objects; dropping the entire entry when one hook matches would silently remove unrelated hooks the user or another tool added to the same entry |
| Remove empty section header after rule removal | Leaves CLAUDE.md clean; a dangling `## Suggested defaults (luca-ops-kit)` header with no content would confuse future audits |
| `rmdir` with `|| true` for luca-ops-kit directory | Only removes the directory if empty (won't accidentally delete user-added files); error suppression is intentional |
| Hooks take effect next session | Platform constraint; user is told explicitly so they know the session they're in still has the hooks active |
| Inline Python/Bash blocks are execution instructions, not user content | Extracting these to external script files would create a file dependency that breaks the skill's self-containment; Claude executes the blocks directly via Bash; the user never sees them |
| Step 2 preview uses manifest text, not live CLAUDE.md state | Verifying live state would add a Read call and create a preview/execute inconsistency if the file changed between preview and execution; Step 3's "absent" reporting handles any drift gracefully |
| Step 2 hook command entry constructed from known pattern, not read from settings.json | The command is always `bash ~/.claude/hooks/<name>.sh`; reading settings.json live would add a tool call and could show a user-modified entry that undo-setup would remove by filename match regardless |
| Fingerprint-not-found triggers a passive note, not a confirmation gate | If a fingerprint is absent from CLAUDE.md, the rule is already gone; the desired end state is already reached; requiring confirmation would add friction with no safety benefit |
| Completeness and Cleanliness are distinct, not overlapping | Completeness = every manifest item was attempted; Cleanliness = no residue remains in the end state; a run can be complete but leave residue (partial write), or clean but incomplete (missing manifest entry) |
