---
name: luca-ops-recommended-setup
description: First-time setup wizard. Checks the user's Claude environment and offers to add two productivity hooks, three generic best-practice rules, and a privacy/backup checklist. Run once after installing luca-ops-kit.
version: 0.1.0
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
| Prompt word count | `prompt-word-count.sh` | `hook2_present` |

**CLAUDE.md rule detection**: search CLAUDE.md text for each fingerprint comment:

| Rule | Fingerprint | Status variable |
|------|-------------|-----------------|
| Use skills first | `<!-- luca-ops-kit:rule-skills-first -->` | `rule1_present` |
| Confirm irreversible | `<!-- luca-ops-kit:rule-confirm-irreversible -->` | `rule2_present` |
| Clarifying question | `<!-- luca-ops-kit:rule-clarifying-question -->` | `rule3_present` |

Carry these six status variables forward. Do not show this step to the user.

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

Write atomically: use Python to write to `~/.claude/CLAUDE.md.tmp`, fsync, then `os.replace()` to the final path. Skip any rule whose fingerprint already exists.

Track which rules were added in a list for the manifest (Step 6).

## Step 5: Offer hooks

If both hooks are already present: tell the user "Your hooks are already configured." and skip to Step 6.

Explain each missing hook in plain language:

**Optimization hint**: after any response that involved many steps, Claude adds a one-sentence note about whether the work could be turned into a reusable skill or pattern. Only fires when there is something worth flagging.

**Clarity check on long prompts**: when you send a message longer than about 50 words, Claude checks whether the desired outcome is clear before diving in. Reduces back-and-forth on ambiguous requests.

Use AskUserQuestion (multiSelect, pre-select missing hooks, include "Skip all hooks" option):
> "Which of these automatic improvements would you like to enable? The plugin's main features work fine without them."

If "Skip all hooks" is chosen, proceed to Step 6.

**Before writing anything**, show the user exactly what will be created:

For each selected hook, display:
- The full file path
- The complete script contents
- The exact JSON entry that will be added to `~/.claude/settings.json`

Use AskUserQuestion (open text):
> "This is exactly what will be added to your system. Type 'yes' to confirm, or describe any changes you'd like."

Only proceed on explicit confirmation.

**Pre-check for idempotent re-runs**: before spawning the reviewer, check whether each selected hook file already exists and is tagged as ours:

```bash
test -f ~/.claude/hooks/<name>.sh && head -2 ~/.claude/hooks/<name>.sh || echo missing
```

- If ALL selected hooks have existing files whose second line contains `# luca-ops-kit:`: this is a full idempotent re-run. Skip the code-reviewer (scripts were reviewed at prior install) and proceed directly to writing.
- Otherwise: spawn the reviewer for all selected scripts (new or untagged files require review).

**When required**, spawn a `feature-dev:code-reviewer` sub-agent. Pass it the full contents of each selected script (shown below) and this prompt:

> Review these shell scripts that will run automatically on every user message in Claude Code.
> (a) Correctness: does each script do exactly what it claims? Trace for edge cases: empty input, malformed JSON, non-UTF-8 characters, very long prompts.
> (b) Security: any command injection, path traversal, or unintended side effects? Scripts receive user message content on stdin; treat as untrusted input.
> (c) Fail-safe: does the script exit 0 on all error paths without printing to stdout?
> (d) Scope: does the script do anything beyond what the user was told?
> Quote offending lines and propose minimal fixes. If no issues, say so explicitly.

If the reviewer flags issues: show them to the user, apply agreed fixes to the script content in this context, then proceed with the corrected versions. If the reviewer is unavailable, note it and continue.

**On confirmation** (and after any reviewer fixes), for each selected hook:

**Check for an existing script file first.** Use Bash to test whether `~/.claude/hooks/<name>.sh` already exists:

```bash
test -f ~/.claude/hooks/<name>.sh && head -2 ~/.claude/hooks/<name>.sh || echo missing
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
# luca-ops-kit:optimization-hint:v1
echo "If this response involved 8+ tool calls, append one 'Optimization hint' at the end (reusable skill, memory-worthy pattern, or workflow improvement). One sentence. Skip if exploratory or one-off."
```

**Hook 2 script** (`~/.claude/hooks/prompt-word-count.sh`):
```bash
#!/bin/bash
# luca-ops-kit:prompt-word-count:v1
command -v python3 >/dev/null || exit 0
word_count=$(cat | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    prompt = data.get('prompt', '') or data.get('user_prompt', '')
    print(len(prompt.split()))
except Exception:
    pass
" 2>/dev/null)
if [ -n "$word_count" ] && [ "$word_count" -gt 50 ] 2>/dev/null; then
  printf 'This prompt is ~%s words. Before starting: confirm the desired outcome is specific enough. If the goal is ambiguous, ask one clarifying question first.\n' "$word_count"
fi
exit 0
```

**settings.json atomic update**: use this Python pattern for each hook:
```python
import json, os, fcntl

script_name = "<name>.sh"
path = os.path.expanduser("~/.claude/settings.json")
try:
    with open(path, "r+") as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        s = json.load(f)
        upsub = s.setdefault("hooks", {}).setdefault("UserPromptSubmit", [])
        already = any(
            script_name in h.get("command", "")
            for entry in upsub for h in entry.get("hooks", [])
        )
        if not already:
            upsub.append({
                "matcher": "",
                "hooks": [{"type": "command", "command": f"bash ~/.claude/hooks/{script_name}"}]
            })
            tmp = path + ".tmp"
            with open(tmp, "w") as tf:
                json.dump(s, tf, indent=2)
                tf.flush()
                os.fsync(tf.fileno())
            os.replace(tmp, path)
except PermissionError:
    # Surface to user; do not write marker
    raise
```

If `~/.claude/settings.json` does not exist, create it with `{"hooks": {"UserPromptSubmit": []}}` first, then apply the update.

If a PermissionError is raised, tell the user: "Cannot write to ~/.claude/settings.json; check file permissions. The hook was not added." Do not write the marker file if any hook write fails.

Only add a hook ID to the manifest list if BOTH the script write and the settings.json update completed without error. Partial installs (one succeeded, one failed) are not recorded; undo-setup should not attempt to reverse a partially applied hook.

## Step 6: Write manifest, marker, and summarize

Write `~/.claude/luca-ops-kit/applied.json` (create directory with `mkdir -p` if needed):

```json
{
  "plugin_version": "0.1.0",
  "applied_at": "<ISO 8601 timestamp from: python3 -c 'from datetime import datetime, timezone; print(datetime.now(timezone.utc).isoformat())'>",
  "rules_added": ["<ids of rules added, e.g. rule-skills-first>"],
  "hooks_added": ["<ids of hooks added, e.g. optimization-hint>"],
  "hooks_backed_up": {
    "<hook-id>": "<absolute backup path, e.g. /Users/.../.claude/hooks/optimization-hint.sh.bak-luca-ops-kit>"
  }
}
```

`hooks_backed_up` is omitted if no backups were made. `/undo-setup` uses it to restore pre-existing scripts rather than deleting them.

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

Spawn a Sonnet sub-agent. Pass it the full contents of this SKILL.md and the following instruction: "Score this skill run on each criterion 0–10. For each, give a one-sentence rationale. Score net of documented design decisions; do not penalise intentional trade-offs listed in ## Design decisions. Return a markdown table; no preamble.":

1. **Detection accuracy**: every item already present was correctly identified and skipped; every missing item was correctly identified and offered
2. **User communication**: explanations in Steps 3–5 are plain enough for a non-technical user to act on without follow-up questions; no developer jargon was surfaced
3. **Safety**: no file was written without explicit user approval; all writes used atomic operations; PermissionError was surfaced and the marker was not written on failure
4. **Manifest accuracy**: `applied.json` exactly reflects what was written: correct IDs, correct backup paths if any, nothing extra or missing

Average ≥ 9.5 → stop. Average < 9.5 → revise and re-score (max 3 iterations; stop if score does not improve). Any criterion < 8 after iteration → draft a concise edit to this SKILL.md, show it to the user, and apply on approval.

## Design decisions

| Decision | Rationale |
|----------|-----------|
| Marker at `~/.claude/luca-ops-kit/setup-complete` (not a root dotfile) | Plugin-namespaced path avoids polluting `~/.claude/` root; survives backup/restore cycles without false triggers |
| Fingerprint comments in CLAUDE.md rules | Enables precise removal by `undo-setup` without content-matching; invisible during normal reading; survives user edits to surrounding text |
| Atomic write + flock for settings.json | Prevents config corruption on crash; guards against two concurrent Claude sessions running setup simultaneously |
| Hook scripts version-tagged in a comment | Allows drift detection on re-run; confirms provenance if user later audits `~/.claude/hooks/` |
| "Skip all hooks" as a first-class option | Non-technical users cannot meaningfully audit shell scripts; making skip prominent respects their agency |
| code-reviewer runs before writing | Reviewer sees the planned script content before any files are touched; fixes are applied in-context and the corrected version is what gets written; avoids inconsistent state from post-write fixes |
| code-reviewer skipped on idempotent re-runs | If all selected hook files already exist and are tagged as ours, the scripts were reviewed at prior install; re-running the reviewer adds no value and wastes a sub-agent call |
| Checklist guarded on re-runs | First-time users need the privacy/backup checklist; returning users who've already read it are interrupted unnecessarily; a one-question gate respects their time |
| Open-text "yes" confirmation for hook preview | Structured multiSelect forces a binary choice; open text lets users say "yes but change the word count threshold" in the same response, reducing round-trips |
| Hook filename search includes `.sh` extension | Searching for `optimization-hint` alone could match a user's unrelated hook that happens to include the word; `.sh` makes the check specific to our exact filename |
| Raw text search for hooks in settings.json (Step 2) | The filename is a JSON string literal and will appear verbatim regardless of indentation or whitespace; only pathological reformatting that splits the filename string (impossible in valid JSON) could cause a false negative; Python parse adds no reliability for this specific case |
| Marker write gated on manifest write success | If the manifest write fails but the marker is written, future re-runs detect "setup complete" but undo-setup finds no manifest and cannot reverse the actual changes; writing marker only after a confirmed manifest write keeps the two files in sync |
| Crash between last hook write and manifest write leaves unrecorded hooks | This is an inherent limitation of sequential multi-step writes without database transactions; re-running setup will detect already-installed hooks via fingerprints and settings.json scan and not re-add them, so the only consequence is the manifest omitting hooks that are already active |
| Fingerprint-present-without-rule is treated as present | A fingerprint comment in CLAUDE.md without its rule body would cause the rule to be skipped on re-run; fingerprint text is highly specific markdown comment syntax that no user would type manually, making this case effectively impossible |
| Backup verified by byte count before overwriting | A failed mid-write backup followed by an overwrite would destroy the original; size verification is a cheap guard that catches this before any data is lost |
| Hook only recorded in manifest if both writes succeed | Partial installs (script written, settings.json failed or vice versa) produce inconsistent state; recording only complete installs ensures undo-setup reverses exactly what is active |
| Manifest written before marker | If the process is interrupted after rules/hooks are written but before the marker, re-run will detect existing items via fingerprints and not duplicate; manifest gives undo-setup a reliable source of truth |
| Hooks take effect next session | Claude Code loads settings.json at startup; this is a platform constraint, not a skill choice; user is told explicitly |
| `prompt-word-count.sh` tries both `prompt` and `user_prompt` keys | The Claude Code hook stdin schema is not publicly documented; the script tries both known key names and silently no-ops if neither matches; a degraded but safe failure; the code-reviewer gate surfaces this concern at install time |
| Existing hook scripts backed up rather than overwritten silently | Overwiting a user's existing hook script without warning destroys their work; backing up preserves it and undo-setup can restore it; the backup path is recorded in the manifest as the source of truth |
| Skills overview is hardcoded (not read from README at runtime) | Avoids a file-read tool call at the end of setup; the table is a stable snapshot that changes only when new skills are added to the plugin, at which point this skill should be updated in the same PR |
