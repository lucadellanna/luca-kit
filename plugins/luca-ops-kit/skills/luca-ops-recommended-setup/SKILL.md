---
name: luca-ops-recommended-setup
description: First-time setup wizard. Checks the user's Claude environment and offers to add an automation hook, three generic best-practice rules, and a privacy/backup checklist. Run once after installing luca-ops-kit.
version: 0.2.0
---

# Recommended Setup

You help users get their Claude environment ready for productive use. Speak in plain language; no developer jargon. Everything you add is reversible with `/undo-setup`.

## Step 1: Check if already run

Use Bash to check whether `~/.claude/luca-ops-kit/setup-complete` exists:

```bash
test -f ~/.claude/luca-ops-kit/setup-complete && echo exists || echo missing
```

- If `exists`: tell the user setup was completed previously and ask whether to re-run or skip. Use AskUserQuestion (multiSelect, options: "Re-run setup", "Skip"):
  > "You've already run setup. Would you like to re-run it or skip?"
  If Skip, stop.
- If `missing`: continue to Step 2.

## Step 2: Audit current state (no user interaction)

Read `~/.claude/settings.json` and `~/.claude/CLAUDE.md`. If either file does not exist, note it and treat all items in that category as missing.

**Hook detection**: search settings.json text for each script filename:

| Hook | Filename to search for | Status variable |
|------|----------------------|-----------------|
| Optimization hint | `optimization-hint.sh` | `hook1_present` |

**CLAUDE.md rule detection**: search CLAUDE.md text for each fingerprint comment:

| Rule | Fingerprint | Status variable |
|------|-------------|-----------------|
| Use skills first | `<!-- luca-ops-kit:rule-skills-first -->` | `rule1_present` |
| Confirm irreversible | `<!-- luca-ops-kit:rule-confirm-irreversible -->` | `rule2_present` |
| Clarifying question | `<!-- luca-ops-kit:rule-clarifying-question -->` | `rule3_present` |

Carry these four status variables forward. Do not show this step to the user.

## Step 3: Manual checklist

If this is a re-run (Step 1 detected the marker), use AskUserQuestion (multiSelect, options: "Yes, show tips", "Skip"):
> "Would you like to see the first-time setup tips again?"
If "Skip": proceed to Step 4 without showing the checklist.

Otherwise, show the checklist below. Frame as informational, not prescriptive:

> **Things you may want to do yourself**
> These are general suggestions. Consult your IT or security team if you work in a managed environment.
>
> 1. **Privacy:** In Claude settings → Privacy, you can disable "Help improve Claude". This prevents your conversations from being used as training data.
> 2. **Backup:** You may want to back up `~/.claude/` to a secure location. This folder contains your skills, memory, and settings; there is no automatic cloud backup. If you back it up, ensure the destination is encrypted and access-controlled.
> 3. **Access control:** Anyone with access to your terminal has full access to your Claude session. On shared or unattended computers, close Claude when you step away.

## Step 4: Offer CLAUDE.md additions

If all three rules are already present (all three `rule*_present` = true): tell the user "Your CLAUDE.md already has the recommended rules." and skip to Step 5.

Explain what each missing rule does, then ask which to add:

| # | Name | What it does |
|---|------|-------------|
| 1 | Use skills before doing manually | Claude checks for an existing skill before starting any multi-step task manually |
| 2 | Confirm before irreversible actions | Claude asks you before sending messages, deleting files, or any action that cannot be undone |
| 3 | Ask one clarifying question when ambiguous | Claude asks one question if your request could mean different things, instead of guessing |

Use AskUserQuestion (multiSelect, pre-select only missing rules):
> "Which of these rules would you like to add to your global Claude settings?"

For each selected rule, add it to the end of `~/.claude/CLAUDE.md` using the atomic write pattern below (read full file → add content → write to .tmp → os.replace; never use open(..., 'a')). Create the file if absent. Create a `## Suggested defaults (luca-ops-kit)` section if absent. Include the fingerprint comment on the same line so undo-setup can find and remove it later:

```
- Before doing any multi-step task manually, check whether a skill exists that covers it. Use the skill if one is found. <!-- luca-ops-kit:rule-skills-first -->
- Always confirm with the user before sending messages, deleting files, submitting forms, or any action that cannot be easily undone. <!-- luca-ops-kit:rule-confirm-irreversible -->
- If a request has multiple valid interpretations, ask one clarifying question before starting. Do not guess at intent. <!-- luca-ops-kit:rule-clarifying-question -->
```

Write atomically: use Python to write to `~/.claude/CLAUDE.md.tmp`, fsync, then `os.replace()` to the final path. If the file does not exist, start with an empty string as the current content (do not raise FileNotFoundError). Skip any rule whose fingerprint already exists.

Track which rules were added in a list for the manifest (Step 6).

## Step 5: Offer hooks

If the hook is already present (`hook1_present` = true): tell the user "Your hook is already configured." and skip to Step 6.

Explain the missing hook in plain language:

**Optimization hint**: after any response that involved many steps, Claude adds a one-sentence note about whether the work could be turned into a reusable skill or pattern. Only fires when there is something worth flagging.

Use AskUserQuestion (multiSelect, options: "Add optimization hint hook", "Skip"):
> "Would you like to enable this automatic improvement? The plugin's main features work fine without it."

If "Skip" is chosen, proceed to Step 6.

**Pre-check for idempotent re-runs**: before spawning the reviewer, check whether each selected hook file already exists and is tagged as ours:

```bash
if test -f ~/.claude/hooks/<name>.sh; then head -2 ~/.claude/hooks/<name>.sh; else echo missing; fi
```

- If ALL selected hooks have existing files whose second line contains `# luca-ops-kit:`: this is a full idempotent re-run. Skip the code-reviewer (scripts were reviewed at prior install) and proceed directly to the preview and confirmation.
- Otherwise: spawn the reviewer for all selected scripts (new or untagged files require review).

**When required**, spawn a `feature-dev:code-reviewer` sub-agent. Pass it the full contents of each selected script (shown below) and this prompt:

> Review these shell scripts that will run automatically on every user message in Claude Code.
> (a) Correctness: does each script do exactly what it claims? Trace for edge cases: empty input, malformed JSON, non-UTF-8 characters, very long prompts.
> (b) Security: any command injection, path traversal, or unintended side effects? Scripts receive user message content on stdin; treat as untrusted input.
> (c) Fail-safe: does the script exit 0 on all error paths without printing to stdout?
> (d) Scope: does the script do anything beyond what the user was told?
> Quote offending lines and propose minimal fixes. If no issues, say so explicitly.

If the reviewer flags issues: apply agreed fixes to the script content in this context before showing the preview to the user. If the reviewer is unavailable, note it and continue.

**Show the user exactly what will be written** (after any reviewer fixes):

For each selected hook, display:
- The full file path
- The complete script contents (post-reviewer version)
- The exact JSON entry that will be added to `~/.claude/settings.json`

Use AskUserQuestion (open text):
> "This is exactly what will be added to your system. Type 'yes' to confirm, or describe any changes you'd like."

Only proceed on explicit confirmation.

**On confirmation**, for each selected hook:

**Check for an existing script file first.** Use Bash to test whether `~/.claude/hooks/<name>.sh` already exists:

```bash
if test -f ~/.claude/hooks/<name>.sh; then head -2 ~/.claude/hooks/<name>.sh; else echo missing; fi
```

- If the file is missing: proceed to write.
- If the file exists and its second line contains `# luca-ops-kit:` (the plugin's version tag): it was written by a previous run of this skill. Proceed to overwrite (idempotent).
- If the file exists and is not tagged as ours: ask the user using AskUserQuestion (multiSelect, options: "Back up and replace", "Skip this hook"):
  > "A file already exists at ~/.claude/hooks/<name>.sh that wasn't created by this plugin. What would you like to do?"
  - **Back up and replace**: copy the existing file to `~/.claude/hooks/<name>.sh.bak-luca-ops-kit` before writing. Internally verify the backup by comparing byte counts (`wc -c` on source and backup (not shown to the user); if they differ, tell the user "Could not back up the existing file; skipping this hook." and treat as Skip. Record the verified backup path in the manifest so `/undo-setup` can restore it.
  - **Skip this hook**: do not write the script; do not add a settings.json entry for this hook; omit it from the manifest.

1. Write the (possibly corrected) script to `~/.claude/hooks/<name>.sh` (create `~/.claude/hooks/` with `mkdir -p` if needed)
2. Set permissions: `chmod 755 ~/.claude/hooks/<name>.sh`
3. Add entry to `~/.claude/settings.json` using atomic write + file lock (see below)

**Hook 1 script** (`~/.claude/hooks/optimization-hint.sh`):
```bash
#!/bin/bash
# luca-ops-kit:optimization-hint:v2
echo "If this response involved 8+ tool calls, append one 'Optimization hint' at the end (reusable skill, memory-worthy pattern, or workflow improvement). One sentence. Skip if exploratory or one-off. Skip if you already captured this pattern in this session (written to memory, code-review checklist, or a CLAUDE.md rule)."
```


**settings.json atomic update**: use this Python pattern for each hook. A dedicated lock file (`settings.json.lock`) is used for synchronization so the lock persists across `os.replace()` calls on the settings file itself.
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
            s = {"hooks": {"UserPromptSubmit": []}}
        except json.JSONDecodeError:
            print("~/.claude/settings.json contains invalid JSON -- cannot modify it safely. Inspect the file and try again.")
            raise SystemExit(1)
        if not isinstance(s, dict):
            print("~/.claude/settings.json is not a JSON object -- cannot modify it safely. Inspect the file and try again.")
            raise SystemExit(1)
        if not isinstance(s.get("hooks"), dict):
            s["hooks"] = {}
        upsub = s["hooks"].setdefault("UserPromptSubmit", [])
        if not isinstance(upsub, list):
            print("~/.claude/settings.json hooks.UserPromptSubmit is not an array -- cannot modify it safely. Inspect the file and try again.")
            raise SystemExit(1)
        already = False
        for entry in upsub:
            if not isinstance(entry, dict):
                continue
            hooks_val = entry.get("hooks", [])
            if not isinstance(hooks_val, list):
                continue
            if any(isinstance(h, dict) and h.get("command") == f"bash ~/.claude/hooks/{script_name}" for h in hooks_val):
                already = True
                break
        if not already:
            upsub.append({
                "matcher": "",
                "hooks": [{"type": "command", "command": f"bash ~/.claude/hooks/{script_name}"}]
            })
            tmp = path + ".tmp"
            try:
                with open(tmp, "w") as tf:
                    json.dump(s, tf, indent=2)
                    tf.write('\n')
                    tf.flush()
                    os.fsync(tf.fileno())
                os.replace(tmp, path)
            except OSError as e:
                print(f"Failed to write ~/.claude/settings.json: {e}. The hook was not added.")
                raise SystemExit(1)
except PermissionError:
    # Surface to user; do not write marker
    raise
```

If a PermissionError is raised, tell the user: "Cannot write to ~/.claude/settings.json; check file permissions. The hook was not added." Do not write the marker file if any hook write fails.

If a JSONDecodeError output is printed, tell the user: "~/.claude/settings.json contains invalid JSON and cannot be safely modified. Inspect the file manually and try again." Do not write the marker file.

If the "is not a JSON object" message is printed, tell the user: "~/.claude/settings.json exists but is not a JSON object (it may be an array or other value). Inspect the file manually and try again." Do not write the marker file.

If the "hooks.UserPromptSubmit is not an array" message is printed, tell the user: "~/.claude/settings.json has an unexpected type for hooks.UserPromptSubmit. Inspect the file manually and try again." Do not write the marker file.

If an OSError output is printed during the write phase, tell the user: "Failed to write to ~/.claude/settings.json. The hook was not added." Do not write the marker file.

Only add a hook ID to the manifest list if BOTH the script write and the settings.json update completed without error. Partial installs (one succeeded, one failed) are not recorded; undo-setup should not attempt to reverse a partially applied hook.

## Step 6: Write manifest, marker, and summarize

Write `~/.claude/luca-ops-kit/applied.json` (create directory with `mkdir -p` if needed).

Build the manifest from **all items currently active** (pre-existing from Step 2 plus anything added in Steps 4–5), not just what was added this run. This makes re-runs self-healing: if a previous run crashed before writing the manifest, the re-run writes a complete manifest covering everything it detects as present.

Before writing: if `~/.claude/luca-ops-kit/applied.json` already exists, read it and extract its entire `hooks_backed_up` map. Copy **all** entries from the old manifest's `hooks_backed_up` into the new manifest, regardless of whether those hook IDs appear in the current `hooks_added` list. Without this merge, a re-run overwrites the manifest and loses backup paths from the prior run; undo-setup would then delete the user's original script instead of restoring it. Use this Python snippet to merge:

```python
import json, os

manifest_path = os.path.expanduser("~/.claude/luca-ops-kit/applied.json")
prior_backed_up = {}
try:
    with open(manifest_path) as f:
        prior = json.load(f)
    if isinstance(prior, dict):
        prior_backed_up = prior.get("hooks_backed_up", {})
        if not isinstance(prior_backed_up, dict):
            prior_backed_up = {}
except (FileNotFoundError, json.JSONDecodeError, AttributeError):
    pass
# Then when building the new manifest, start hooks_backed_up from prior_backed_up
# and add any new backup paths recorded during this run on top of it.
```

Build the manifest dict using the structure above, then write it atomically:

```python
import json, os

manifest_path = os.path.expanduser("~/.claude/luca-ops-kit/applied.json")
os.makedirs(os.path.dirname(manifest_path), exist_ok=True)
manifest = {
    "plugin_version": "0.1.0",
    "applied_at": applied_at,      # ISO 8601 string from datetime.now(timezone.utc).isoformat()
    "rules_added": rules_added,    # list of all active rule IDs
    "hooks_added": hooks_added,    # list of all active hook IDs
}
if hooks_backed_up:
    manifest["hooks_backed_up"] = hooks_backed_up  # merged from prior + this run
tmp = manifest_path + ".tmp"
try:
    with open(tmp, "w") as tf:
        json.dump(manifest, tf, indent=2)
        tf.write('\n')
        tf.flush()
        os.fsync(tf.fileno())
    os.replace(tmp, manifest_path)
except OSError as e:
    print(f"Could not write manifest: {e}")
    raise SystemExit(1)
```

`hooks_backed_up` is omitted when neither this run nor any prior run backed up a script. On re-runs, previously recorded backup paths are carried forward from the prior manifest, so the key may be present even if the current run made no new backups. `/undo-setup` uses it to restore pre-existing scripts rather than deleting them.

If the manifest write fails, tell the user "Could not write the setup record; setup is incomplete. Run `/luca-ops-recommended-setup` again to retry." Do not write the marker.

If the manifest write succeeds, write the marker:
```bash
mkdir -p ~/.claude/luca-ops-kit && touch ~/.claude/luca-ops-kit/setup-complete
```

Tell the user:
- What was added (rules and hooks, or "nothing new: already configured")
- That hooks take effect next time Claude starts
- "To remove everything this setup added, run `/undo-setup` before uninstalling the plugin."
- Remind them the manual checklist items from Step 3 still need their attention

Then present the full skill overview:

> **What you can do with luca-ops-kit**
>
> | Skill | What it does |
> |-------|-------------|
> | `/luca-ops-recommended-setup` | First-run wizard: adds best-practice rules and automation hooks to your Claude environment |
> | `/undo-setup` | Reverses everything `/luca-ops-recommended-setup` added so you can cleanly uninstall the plugin |
> | `/build-work-context` | Interviews you about your company and role, then saves a persistent profile so Claude doesn't need to ask "who do you work for?" every session |
> | `/create-skill` | Turns a procedure, SOP, checklist, or verbal description into a ready-to-use skill file, scoring and improving it before saving |
> | `/list-skills` | Lists every installed skill with its plugin, one-line description, and file size in a single table |
> | `/audit-skill` | Scores a single skill against 7 quality dimensions, proposes improvements, and iterates until the bar is met |
> | `/audit-skills` | Scans your whole skill library for overlapping skills, then audits a rotating batch of 3 so every skill gets reviewed over time |
> | `/audit-claude` | Scans your CLAUDE.md and memory files for bloat and redundancy, proposes targeted cuts, and verifies nothing meaningful was lost |
> | `/reflect` | After a session, extracts what went well, what went wrong, and what should become a memory update, skill improvement, or new skill |
> | `/dream` | Mines your `/reflect` logs to surface patterns across sessions: recurring issues, memory contradictions, and improvements that keep coming up |

## Self-reflection

During execution, follow the self-observation protocol (see CLAUDE.md Principles).

Spawn a Haiku sub-agent. Pass it the full contents of this SKILL.md and the following instruction: "Score this skill run on each criterion 0–10. For each, give a one-sentence rationale. Return a markdown table; no preamble.":

1. **Detection accuracy**: every item already present was correctly identified and skipped; every missing item was correctly identified and offered
2. **User communication**: explanations in Steps 3–5 are plain enough for a non-technical user to act on without follow-up questions; no developer jargon was surfaced
3. **Safety**: no file was written without explicit user approval; all writes used atomic operations; PermissionError was surfaced and the marker was not written on failure
4. **Manifest accuracy**: `applied.json` exactly reflects what was written: correct IDs, correct backup paths if any, nothing extra or missing

Average ≥ 9.5 → stop. Average < 9.5 → revise and re-score (max 3 iterations; stop if score does not improve). Any criterion < 8 after iteration → draft a concise edit to this SKILL.md, show it to the user, and apply on approval.

