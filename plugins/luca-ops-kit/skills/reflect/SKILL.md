---
name: reflect
description: >
  Use this skill when the user says "reflect", "let's reflect", or asks to
  analyze the current conversation for learning points, errors, and improvement
  opportunities. Scans tasks, errors, user feedback, and workflow patterns to
  extract actionable insights. Can write learnings to memory and propose
  improvements to the plugin's own skills.
version: 0.2.0
---

# Reflect

Analyze the current conversation to extract learning points, catch errors, and detect opportunities for skill creation or improvement. Present findings and act on what the user chooses.

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

## Step 1: Scan and Extract

**CRITICAL**: Do not restate what happened in the conversation. The goal is to extract learnings and improvements, not to summarize the task.

Review the full conversation. For each noteworthy item, capture: what happened (one sentence), why it matters, and a specific actionable takeaway. Discard trivial items.

Scan these areas:

- **Tasks completed**: what was asked for, what was delivered, whether accepted or revised
- **Errors and corrections**: Claude mistakes, user pushback (explicit: "no, I meant..."; implicit: rephrasing, abandoning a line); positive signals too (accepted, praised, built on)
- **Workflow patterns**: repeated sequences, tool chains, procedures done more than twice in a similar way
- **Knowledge gaps**: things Claude got wrong, had to look up, or where the user supplied domain knowledge Claude lacked
- **External reviewer patterns**: did any automated reviewer (Gemini, sub-agent) flag the same issue category 2+ times? Each recurring catch is a candidate for a new checklist item or class-level rule
- **User workflow**: steps the user took repeatedly or awkwardly that a skill, shortcut, or process change could streamline; opportunities the user might not notice themselves
- **Time efficiency**: steps or sequences where the user spent disproportionate time relative to the value gained; identify specifically what took longer than it should have and what a faster path would look like (different tool, reversed order, delegated to Claude earlier, skipped entirely)

## Step 2: Classify Findings

Classify each finding into one action category:

**Write to memory**: Context, preferences, or knowledge that should persist. Examples: "User prefers concise output", "When user says 'post' without qualifier, they mean LinkedIn". For each memory finding, also identify the target memory file and section (e.g., `feedback_testing.md:rule-3`); this field is used for contradiction detection in /dream.

**Create a new skill**: A reusable procedure that doesn't exist yet. Must meet three criteria: (1) would apply more than once, (2) has clear inputs and outputs, (3) is complex enough that instructions help.

**Improve an existing skill**: A skill produced suboptimal results, missed an edge case, or could be extended. Reference the specific skill name and the specific change.

**No action needed**: Worth noting as an insight but doesn't warrant a persistent change.

## Step 3: Score and Revise

Spawn a Haiku sub-agent to score the current findings. Pass it:
1. The full findings list
2. These criteria and their definitions
3. The instruction: "Score each criterion 0–10. For each, give a one-sentence rationale. Return a markdown table."

Criteria:
1. **Precision**: each finding is scoped correctly: not too broad ("Claude made mistakes") nor too narrow (a single-message detail that doesn't generalise)
2. **Non-triviality**: no generic observations that apply to any conversation
3. **Concreteness**: every actionable finding names a specific next step that can be executed immediately
4. **Coverage**: no obvious patterns or errors from the conversation were missed
5. **Accuracy**: each finding is factually grounded: the events, errors, and patterns described actually occurred as stated in the conversation

Use the sub-agent's scores directly. If average < 9.5, revise the findings and re-score. Stop after 3 iterations or if the score stops improving (< 0.5 gain counts as stagnant; one extra iteration allowed if prior changes were substantive). Do not present findings until the threshold is met or iterations are exhausted.

## Step 4: Present Findings

Present grouped by action category. Omit empty categories. Mark each item **High** or **Medium** priority.

- **Insights**: Findings worth noting, 1-2 sentences each.
- **Suggested Memory Updates**: What to remember and why.
- **Skill Opportunities**: Proposed name, purpose, trigger, why it's worth creating.
- **Skill Improvements**: Which skill, what's wrong, the specific change.

Ask the user what to implement via AskUserQuestion (multiSelect: true) with the specific items as options.

## Step 5: Act on Choices

**Memory updates**: State the exact text to be added (one or two lines), then write it to `.claude/memory/MEMORY.md` under `## Preferences` or `## Context` (create file/section if needed). Terse entries only; just what Claude needs to know.

**New skills**: Run `/create-skill` with the proposed name, purpose, and trigger as context.

**Skill improvements**: State the planned edit (one line), then apply it. One focused edit per finding.

## Step 5b: Append log entry

Runs after Step 5. Run only if `~/.claude/reflect-logs/.enabled` exists.

**Derive repo slug** using Python (all subprocess calls ignore errors):
```
1. git remote get-url origin  →  strip trailing slash, strip .git suffix,
   normalize colons to slashes, take last 2 path components, join with "__"  →  "org__repo"
2. Fallback: basename of git rev-parse --show-toplevel
3. Fallback: "no-repo"
Sanitize: replace chars outside [a-zA-Z0-9_-] with "-"
```

**Build and append entry** using `python3` for atomic write (prevents partial lines). Includes the double-log guard: prints `DUPLICATE_DATE` and exits without writing if today's date is already in the log.

```python
import json, os, sys, datetime, subprocess

def run(cmd):
    try:
        return subprocess.run(cmd, capture_output=True, text=True).stdout.strip()
    except FileNotFoundError:
        return ""

origin = run(['git', 'remote', 'get-url', 'origin'])
if origin:
    clean = origin.rstrip('/')
    if clean.endswith('.git'): clean = clean[:-4]
    slug = '__'.join(clean.replace(':', '/').split('/')[-2:])
else:
    top = run(['git', 'rev-parse', '--show-toplevel'])
    slug = os.path.basename(top) or 'no-repo' if top else 'no-repo'
slug = ''.join(c if c.isalnum() or c in '-_' else '-' for c in slug)

branch = run(['git', 'branch', '--show-current']) or run(['git', 'rev-parse', '--short', 'HEAD']) or 'unknown'

path = os.path.expanduser(f"~/.claude/reflect-logs/{slug}.jsonl")
os.makedirs(os.path.dirname(path), exist_ok=True)
today = str(datetime.date.today())
allow_dup = os.environ.get('ALLOW_DUPLICATE', '').lower() in ('1', 'true', 'yes')
count = 0
try:
    with open(path) as f:
        for line in f:
            try:
                obj = json.loads(line)
                if not allow_dup and isinstance(obj, dict) and obj.get('date') == today:
                    print('DUPLICATE_DATE')
                    sys.exit(0)
                count += 1
            except json.JSONDecodeError:
                pass
except FileNotFoundError:
    pass
count += 1

entry = {
    "schema": 1,
    "date": today,
    "branch": branch,
    "workspace": "/".join(os.path.normpath(os.getcwd()).split(os.sep)[-2:]),
    "findings": [
        # One object per finding from Step 2 (all findings, not just acted-on):
        # { "id": 1,                             # sequential integer within this entry
        #   "type": "memory|skill_improvement|new_skill|no_action",
        #   "category": "error|workflow|knowledge_gap|tool_friction|other",
        #   "text": "<one-line description>",
        #   "memory_target": "<file:section>",   # memory type only
        #   "skill": "<name>",                   # skill_improvement type only
        #   "change": "<summary>" }              # skill_improvement type only
    ],
    "actions_taken": [
        # One object per action actually applied in Step 5:
        # { "type": "memory|improve_skill|create_skill",
        #   "target": "<file or skill name>",
        #   "finding_id": 1 }                    # id of the finding this action resolved
    ],
    "avg_score": 0.0  # replace with avg_score from Step 3
}

with open(path, 'a') as f:
    f.write(json.dumps(entry) + '\n')
if count >= 10 and count % 10 == 0:
    print(f"NUDGE:{count}")
```

If the script prints `DUPLICATE_DATE`: ask "You've already logged a reflection today. Add a second entry, or skip?" (default: skip). If the user chooses to add a second entry, re-run with `ALLOW_DUPLICATE=1 python3 -c '...'`.

If the script prints `NUDGE:<count>`, append to end of output:
> "You've completed `<count>` /reflect sessions; a good moment to run /dream, which spots patterns across sessions and consolidates memory. (Don't have /dream yet? It's part of the luca-ops-kit plugin.)"

## Self-reflection

During execution, follow the self-observation protocol (see CLAUDE.md Principles).

After acting on choices, spawn a Haiku sub-agent to verify:

1. **Impact**: if any actions were selected: at least one was successfully applied. Auto-pass if the user declined all proposed actions or only insights were surfaced.
2. **Quality**: auto-pass if all 3 scoring iterations were completed, regardless of final average; also passes if average ≥ 9.5 was reached in fewer iterations.
3. **No overreach**: no actions were taken beyond what the user selected

If any criterion scores below 8, draft a concise edit to this SKILL.md to prevent the same failure, show it to the user, and apply on approval.

## Where the data lives

Session notes are saved to `~/.claude/reflect-logs/<project-name>.jsonl`, one line per session.

Each line contains findings and scores from that session. Findings may include short excerpts from the conversation. Notes never enter any git repository and never leave your computer unless you copy the file.

- To stop saving notes: say "disable session notes" at any time.
- To view notes: open the file in any text editor, or run `cat ~/.claude/reflect-logs/<project>.jsonl`.
- To delete all notes for a project: `rm ~/.claude/reflect-logs/<project>.jsonl`.
- To disable permanently: `rm ~/.claude/reflect-logs/.enabled && touch ~/.claude/reflect-logs/.disabled`.
