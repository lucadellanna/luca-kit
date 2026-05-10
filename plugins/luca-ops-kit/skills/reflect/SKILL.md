---
name: reflect
description: >
  Use this skill when the user says "reflect", "let's reflect", or asks to
  analyze the current conversation for learning points, errors, and improvement
  opportunities. Scans tasks, errors, user feedback, and workflow patterns to
  extract actionable insights. Can write learnings to memory and propose
  improvements to the plugin's own skills.
version: 0.3.0
---

# Reflect

Analyze the current conversation to extract learning points, catch errors, and detect opportunities for skill creation or improvement. Present findings immediately; the user is the quality gate.

## Step 0: Pre-flight checks

**Length check:** If the conversation has fewer than ~5 substantive exchanges, say "Not enough material to reflect on meaningfully" and stop. Do not run the logging opt-in.

**Logging opt-in** (only if proceeding past the length check):

```bash
ls -A ~/.claude/reflect-logs/ 2>/dev/null | grep -E '^\.(en|dis)abled$'
```

- `.enabled` found: logging is on. Proceed.
- `.disabled` found: logging is off. Proceed silently.
- Neither found: ask once using AskUserQuestion (singleSelect):

  "Can I save a private note about what we learned in this session? Future sessions can then spot patterns over time. The note stays on your computer only.

  - Yes, save session notes
  - No thanks, never ask again
  - Skip for now (ask me next time)"

  Apply:
  - Yes: `mkdir -p ~/.claude/reflect-logs && touch ~/.claude/reflect-logs/.enabled`
  - No: `mkdir -p ~/.claude/reflect-logs && touch ~/.claude/reflect-logs/.disabled`
  - Skip: continue without logging

## Step 1: Scan, Extract, and Classify

**CRITICAL**: Do not restate what happened in the conversation. Extract learnings and improvements only.

Review the full conversation. For each noteworthy item, capture: what happened (one sentence), why it matters, and a specific actionable takeaway.

Scan areas (skip any that have no signal; never write filler findings):

- **Errors and corrections**: Claude mistakes, user pushback, positive signals
- **Workflow patterns**: repeated sequences, procedures done more than twice
- **Knowledge gaps**: things Claude got wrong or the user had to supply
- **User workflow**: steps the user took repeatedly or awkwardly that a skill or process change could streamline

Classify each finding into one action category:

- **Write to memory**: Context, preferences, or knowledge that should persist.
- **Create a new skill**: A reusable procedure that doesn't exist yet. Must: (1) apply more than once, (2) have clear inputs/outputs, (3) be complex enough that instructions help.
- **Improve an existing skill**: Reference the specific skill and change.
- **No action needed**: Worth noting as insight but no persistent change needed.

## Step 2: Present Findings

Present grouped by action category. Omit empty categories. Mark each item **High** or **Medium** priority.

- **Insights**: Findings worth noting, 1-2 sentences each.
- **Suggested Memory Updates**: What to remember and why.
- **Skill Opportunities**: Proposed name, purpose, trigger, why it's worth creating.
- **Skill Improvements**: Which skill, what's wrong, the specific change.

Ask the user what to implement via AskUserQuestion (multiSelect: true) with the specific items as options.

## Step 3: Act on Choices

**Memory updates**: State the exact text (one or two lines), then write to `.claude/memory/MEMORY.md` under `## Preferences` or `## Context` (create file/section if needed). Terse entries only.

**New skills**: Run `/create-skill` with the proposed name, purpose, and trigger as context.

**Skill improvements**: State the planned edit (one line), then apply it.

## Step 4: Log session

Runs after Step 3. Run only if `~/.claude/reflect-logs/.enabled` exists.

```python
import json, os, datetime, subprocess

def run(cmd):
    try: return subprocess.run(cmd, capture_output=True, text=True).stdout.strip()
    except FileNotFoundError: return ""

origin = run(['git', 'remote', 'get-url', 'origin'])
if origin:
    clean = origin.rstrip('/'); clean = clean[:-4] if clean.endswith('.git') else clean
    slug = '__'.join(clean.replace(':', '/').split('/')[-2:])
else:
    top = run(['git', 'rev-parse', '--show-toplevel'])
    slug = os.path.basename(top) or 'no-repo' if top else 'no-repo'
slug = ''.join(c if c.isalnum() or c in '-_' else '-' for c in slug)

path = os.path.expanduser(f"~/.claude/reflect-logs/{slug}.jsonl")
os.makedirs(os.path.dirname(path), exist_ok=True)
entry = {
    "schema": 2,
    "date": str(datetime.date.today()),
    "findings": [
        # One string per finding from Step 1, e.g.:
        # "error: Claude assumed X without verifying"
        # "pattern: user always does Y before Z"
    ]
}
with open(path, 'a') as f:
    f.write(json.dumps(entry) + '\n')
```

## Where the data lives

Session notes are saved to `~/.claude/reflect-logs/<project-name>.jsonl`, one line per session. Each line contains the date and a list of finding strings.

- To stop saving notes: say "disable session notes" at any time.
- To view notes: `cat ~/.claude/reflect-logs/<project>.jsonl`
- To delete all notes for a project: `rm ~/.claude/reflect-logs/<project>.jsonl`
- To disable permanently: `rm ~/.claude/reflect-logs/.enabled && touch ~/.claude/reflect-logs/.disabled`
