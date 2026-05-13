---
name: reflect
description: >
  Use this skill when the user says "reflect", "let's reflect", or asks to
  analyze the current conversation for learning points, errors, and improvement
  opportunities. Scans tasks, errors, user feedback, and workflow patterns to
  extract actionable insights. Can write learnings to memory and propose
  improvements to the plugin's own skills.
version: 0.4.0
---

# Reflect

Analyze the current conversation to extract learning points, catch errors, and detect opportunities for skill creation or improvement. Present findings immediately; the user is the quality gate.

## Step 0: Pre-flight checks

**Length check:** If the conversation has fewer than ~5 substantive exchanges, say "Not enough material to reflect on meaningfully" and stop. Do not run the logging check.

**Logging check** (only if proceeding past the length check):

```bash
ls -A ~/.claude/reflect-logs/ 2>/dev/null | grep -E '^\.(en|dis)abled$'
```

- `.enabled` found (regardless of whether `.disabled` also exists): logging is on. Proceed.
- Only `.disabled` found: logging is off. Proceed silently.
- Neither found: tell the user once: "Session notes aren't configured yet. Run `/luca-reflection-kit:luca-reflection-recommended-setup` to decide; it takes 10 seconds. Proceeding without notes for now." Then continue.

## Step 1: Scan, Extract, and Classify

**CRITICAL**: Do not restate what happened in the conversation. Extract learnings and improvements only.

Review the full conversation. For each noteworthy item, capture: what happened (one sentence), why it matters, and a specific actionable takeaway.

Scan areas (skip any that have no signal; never write filler findings):

- **Errors and corrections**: Claude mistakes, user pushback, positive signals
- **Workflow patterns**: repeated sequences, procedures done more than twice
- **Knowledge gaps**: things Claude got wrong or the user had to supply
- **User workflow**: steps the user took repeatedly or awkwardly that a skill or process change could streamline
- **Unnecessary questions**: moments where Claude asked the user for input that Claude could and should have decided itself (e.g. asking which of two equivalent approaches to use, asking for confirmation on a low-stakes reversible action, asking for information already inferable from context). For each instance: identify what Claude asked, what decision rule would have avoided the question, and whether a skill or CLAUDE.md rule should encode that rule.

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

**Memory updates**: Before writing, check whether the learning is already covered by an existing rule in global or project CLAUDE.md. If it is, skip the write and note which rule already covers it. Otherwise, state the exact text (one or two lines), then write to `.claude/memory/MEMORY.md` under `## Preferences` or `## Context` (create file/section if needed). Terse entries only.

**New skills**: Run `/create-skill` with the proposed name, purpose, and trigger as context.

**Skill improvements**: State the planned edit (one line), then apply it.

## Step 4: Log session

Runs after Step 3.

First, check whether session notes are enabled:

```bash
ls ~/.claude/reflect-logs/.enabled 2>/dev/null && echo "enabled" || echo "skip"
```

If `skip`, stop silently. Do not check for python3 or run the script.

If `enabled`, check python3:

```bash
command -v python3 >/dev/null 2>&1 && echo "ok" || echo "missing"
```

If `missing`, tell the user: "Session notes couldn't be saved: Python 3 isn't installed. Get it from python.org when ready." Then stop.

If `ok`, build a JSON array of the findings from Step 1 (one string per finding, e.g. `"error: Claude assumed X"`, `"pattern: user always does Y"`). Then run:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/log-session.py" <<'FINDINGS'
["finding 1", "finding 2"]
FINDINGS
```

Replace the array content with actual findings. Use standard JSON string escaping (backslash for internal quotes and backslashes).

## Where the data lives

Session notes are saved to `~/.claude/reflect-logs/<project-name>.jsonl`, one line per session. Each line contains the date and a list of finding strings.

- To stop saving notes: say "disable session notes" at any time.
- To view notes: `cat ~/.claude/reflect-logs/<project>.jsonl`
- To delete all notes for a project: `rm ~/.claude/reflect-logs/<project>.jsonl`
- To disable permanently: `rm ~/.claude/reflect-logs/.enabled && touch ~/.claude/reflect-logs/.disabled`
