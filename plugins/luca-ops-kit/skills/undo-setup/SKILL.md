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

Read `~/.claude/CLAUDE.md` once. If the file does not exist, note it and skip this step.

In a single pass over the file lines:
- For each line, check whether it contains any of the fingerprint comments from `rules_added` (e.g., `<!-- luca-ops-kit:rule-skills-first -->`). Remove lines that match.
- Track which fingerprints were found and which were absent.

After filtering all lines: check if the `## Suggested defaults (luca-ops-kit)` section header has no bullet lines remaining under it. If the header is now empty, remove it too.

Write the result back atomically in one operation: write to `~/.claude/CLAUDE.md.tmp`, fsync, then `os.replace()`.

Report any fingerprints that were not found: "Rule already absent: <id>".

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
try:
    with open(path, "r+") as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        s = json.load(f)
        upsub = s.get("hooks", {}).get("UserPromptSubmit", [])
        new_upsub = []
        changed = False
        for entry in upsub:
            remaining = [h for h in entry.get("hooks", []) if script_name not in h.get("command", "")]
            if len(remaining) != len(entry.get("hooks", [])):
                changed = True
                if remaining:
                    new_upsub.append({**entry, "hooks": remaining})
                # else: entry has no hooks left; drop it entirely
            else:
                new_upsub.append(entry)
        if changed:
            s["hooks"]["UserPromptSubmit"] = new_upsub
            tmp = path + ".tmp"
            with open(tmp, "w") as tf:
                json.dump(s, tf, indent=2)
                tf.flush()
                os.fsync(tf.fileno())
            os.replace(tmp, path)
except FileNotFoundError:
    pass  # settings.json already gone; nothing to remove
except PermissionError:
    print(f"Cannot write to {path} -- check permissions.")
    raise
```

If PermissionError, tell the user and stop without writing the remaining steps.

## Step 5: Remove or restore hook scripts

For each hook ID in `hooks_added`:

Check the manifest for a `hooks_backed_up` entry mapping the hook ID to a backup path (e.g., `~/.claude/hooks/<name>.sh.bak-luca-ops-kit`). This entry is written when `/luca-ops-recommended-setup` backed up a pre-existing file before overwriting.

- **If a backup path is recorded**: restore it. Use Bash to run:
  ```bash
  mv ~/.claude/hooks/<name>.sh.bak-luca-ops-kit ~/.claude/hooks/<name>.sh
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
| Atomic write + flock for settings.json | Same reason as in luca-ops-recommended-setup: prevents corruption on crash or concurrent access |
| Hook removal filters within entries, not whole entries | A UserPromptSubmit entry can contain multiple hook objects; dropping the entire entry when one hook matches would silently remove unrelated hooks the user or another tool added to the same entry |
| Remove empty section header after rule removal | Leaves CLAUDE.md clean; a dangling `## Suggested defaults (luca-ops-kit)` header with no content would confuse future audits |
| `rmdir` with `|| true` for luca-ops-kit directory | Only removes the directory if empty (won't accidentally delete user-added files); error suppression is intentional |
| Hooks take effect next session | Platform constraint; user is told explicitly so they know the session they're in still has the hooks active |
| Inline Python/Bash blocks are execution instructions, not user content | Extracting these to external script files would create a file dependency that breaks the skill's self-containment; Claude executes the blocks directly via Bash; the user never sees them |
| Step 2 preview uses manifest text, not live CLAUDE.md state | Verifying live state would add a Read call and create a preview/execute inconsistency if the file changed between preview and execution; Step 3's "absent" reporting handles any drift gracefully |
| Fingerprint-not-found triggers a passive note, not a confirmation gate | If a fingerprint is absent from CLAUDE.md, the rule is already gone; the desired end state is already reached; requiring confirmation would add friction with no safety benefit |
| Completeness and Cleanliness are distinct, not overlapping | Completeness = every manifest item was attempted; Cleanliness = no residue remains in the end state; a run can be complete but leave residue (partial write), or clean but incomplete (missing manifest entry) |
