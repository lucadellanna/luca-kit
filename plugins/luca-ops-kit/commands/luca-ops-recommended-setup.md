---
description: First-time setup wizard. Adds best-practice rules and shows a privacy/backup checklist. Run once after installing luca-ops-kit.
---

# Recommended Setup

You help users get their Claude environment ready for productive use. Speak in plain language; no developer jargon. Everything you add is reversible with `/undo-setup`.

## Step 1: Check if already run

Use Bash to check whether `~/.claude/luca-ops-kit/setup-complete` exists:

```bash
test -f ~/.claude/luca-ops-kit/setup-complete && echo exists || echo missing
```

- If `exists`: tell the user setup was completed previously and ask whether to re-run or skip. Use AskUserQuestion (singleSelect, options: "Re-run setup", "Skip"):
  > "You've already run setup. Would you like to re-run it or skip?"
  If Skip, stop.
- If `missing`: continue to Step 2.

## Step 2: Audit current state (no user interaction)

Read `~/.claude/CLAUDE.md`. If the file does not exist, treat all rules as missing.

Search CLAUDE.md text for each fingerprint comment:

| Rule | Fingerprint | Status variable |
|------|-------------|-----------------|
| Use skills first | `<!-- luca-ops-kit:rule-skills-first -->` | `rule1_present` |
| Confirm irreversible | `<!-- luca-ops-kit:rule-confirm-irreversible -->` | `rule2_present` |
| Clarifying question | `<!-- luca-ops-kit:rule-clarifying-question -->` | `rule3_present` |

Carry these three status variables forward. Do not show this step to the user.

## Step 3: Manual checklist

If this is a re-run (Step 1 detected the marker), use AskUserQuestion (singleSelect, options: "Yes, show tips", "Skip"):
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

Write atomically: use Python with `os.path.expanduser("~/.claude/CLAUDE.md")` as the path. Write to `.tmp`, fsync, then `os.replace()` to the final path. If the file does not exist, start with an empty string as the current content (do not raise FileNotFoundError). Skip any rule whose fingerprint already exists.

## Step 5: Write marker and summarize

Write the setup-complete marker:
```bash
mkdir -p ~/.claude/luca-ops-kit && touch ~/.claude/luca-ops-kit/setup-complete
```

If the marker write fails, tell the user and stop.

Tell the user:
- What was added (rules, or "nothing new: already configured")
- "To remove the rules this setup added, run `/undo-setup`."
- Remind them the manual checklist items from Step 3 still need their attention

Then present the full skill overview:

> **What you can do with luca-ops-kit**
>
> | Skill | What it does |
> |-------|-------------|
> | `/luca-ops-recommended-setup` | First-run wizard: adds best-practice rules to your Claude environment |
> | `/undo-setup` | Reverses everything `/luca-ops-recommended-setup` added |
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

Spawn a Haiku sub-agent. Read `$CLAUDE_PLUGIN_ROOT/commands/luca-ops-recommended-setup.md` and pass its contents with the following instruction: "Score this command run on each criterion 0-10. For each, give a one-sentence rationale. Return a markdown table; no preamble.":

1. **Detection accuracy**: every rule already present was correctly identified and skipped; every missing rule was correctly identified and offered
2. **User communication**: explanations in Steps 3-4 are plain enough for a non-technical user to act on without follow-up questions; no developer jargon was surfaced
3. **Safety**: no file was written without explicit user approval; all writes used atomic operations; errors were surfaced and the marker was not written on failure

Average >= 9.5 -> stop. Average < 9.5 -> revise and re-score (max 3 iterations; stop if score does not improve). Any criterion < 8 after iteration -> draft a concise edit to this file, show it to the user, and apply on approval.
