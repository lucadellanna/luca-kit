---
name: reflect
description: >
  Use this skill when the user says "reflect", "let's reflect", or asks to
  analyze the current conversation for learning points, errors, and improvement
  opportunities. Orchestrates two reviewers in parallel over a verbatim
  conversation digest, auto-applies safe changes to project memory, asks the
  user about anything riskier, and surfaces a few user-facing hints.
version: 0.6.0
---

# Reflect

Orchestrator. Gathers inputs, runs two reviewers in parallel, computes risk from each finding's target file, auto-applies the safe ones, asks about the rest, surfaces user hints, logs the session.

You are not a reviewer. The reviewers are sub-agents. Your job is to gather, route, apply, and log.

## Step 1: Gather inputs

### 1a. Conversation digest

Construct a verbatim digest of conversation turns since the last `/reflect` in this session (or session start). To locate the boundary, scan backward through conversation turns for the most recent turn where the user message matches the reflect trigger phrases; the digest starts with the turn immediately after that. Format:

```
--- Turn N ---
[user]
<verbatim user message>

[claude tool: <tool-name>(<args summary>)]
<tool output: first 5 lines + "[... K lines omitted ...]" + last 5 lines if longer>

[claude]
<verbatim Claude response text>
```

No interpretation, no labels. Just turns. Tool outputs truncated to 5 + 5 lines. Code blocks and file contents inside Claude responses stay as-is.

### 1b. Rule corpus

Reviewers cannot read files. Assemble the full rule corpus once:

```bash
echo "=== PROJECT MEMORY ==="
cat .claude/memory/MEMORY.md 2>/dev/null || echo "(absent)"
echo
echo "=== GLOBAL CLAUDE.md (~/.claude/CLAUDE.md) ==="
cat ~/.claude/CLAUDE.md 2>/dev/null || echo "(absent)"
echo
echo "=== PROJECT CLAUDE.md (./CLAUDE.md) ==="
cat CLAUDE.md 2>/dev/null || echo "(absent)"
echo
echo "=== PLUGIN RUNTIME CLAUDE.md (\${CLAUDE_PLUGIN_ROOT}/CLAUDE.md) ==="
cat "${CLAUDE_PLUGIN_ROOT}/CLAUDE.md" 2>/dev/null || echo "(absent)"
```

### 1c. Skills + commands index

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/enumerate-skills.py"
```

Hold the digest, rule corpus, and index in working memory for Step 2.

## Step 2: Run two reviewers in parallel

Send a single message with two `Agent` calls:

- `subagent_type: "luca-reflection-kit:claude-flow-reviewer"`: behavior-asset reviewer (Agent 1).
- `subagent_type: "luca-reflection-kit:user-flow-reviewer"`: user-hint reviewer (Agent 2).

Inline all three inputs verbatim into each Agent call prompt in this order: (1) the conversation digest under the heading `## Conversation digest`, (2) the rule corpus under `## Rule corpus`, (3) the skills + commands index under `## Skills index`.

Each agent's mandate, finding categories, and output format are defined in the agent's own file. Do not duplicate them here.

If both reviewers return nothing, write a one-line message ("Nothing worth surfacing.") and proceed to Step 7 to log the empty session. If one returns nothing, note that in the report header and proceed with the other.

## Step 3: Assign risk to Agent 1 findings

Each Agent 1 finding has a `target` file path. Map `target` → `risk`:

| Target | Risk |
|---|---|
| Project `.claude/memory/MEMORY.md` or global `~/.claude/MEMORY.md` | `safe` |
| Any `CLAUDE.md` (project, global, plugin runtime) | `ambiguous` |
| Any existing skill file | `ambiguous` |
| New skill creation (path that does not yet exist) | `ambiguous` |
| Hook script (`.sh`, `.py` under `hooks/`) | `security-sensitive` |
| Anything else | `breaking` |

Before assigning the "New skill creation" row, check whether the path exists: `test -f <target> && echo exists || echo absent`. Apply that row only when the file is absent; use "Any existing skill file" when it exists.

The orchestrator computes risk. The agent does not.

## Step 4: Auto-apply safe findings

Auto-apply requires both:
- `risk = safe` (computed in Step 3), AND
- `proposed_change` is a plain text addition (no line in `proposed_change` starts with `edit:` or `new skill at`).

Findings with `risk = safe` but an `edit:` or `new skill at` shape are routed into Step 5 (ask) regardless of target. Auto-apply only writes new lines; rewriting existing lines or creating new files always asks.

For each eligible finding:

1. Read the target file. If `proposed_change` is a single line, check with `grep -qF`; if it spans multiple lines, check as a substring of the full file content. Skip and note as duplicate if a match is found.
2. Otherwise append the proposed text as a new line at the end of the target file. If the file does not exist, create it with the proposed text as the first line.
3. Record success or failure for Step 6.

## Step 5: Ask the user about non-safe findings

Collect Agent 1 findings with `risk` in `{ambiguous, breaking, security-sensitive}`. If more than 4, keep the top 4 ordered by risk level (`security-sensitive` first, then `breaking`, then `ambiguous`), then by order returned; the rest go to "Logged only".

If the count is zero, skip this step.

Otherwise call `AskUserQuestion` (`multiSelect: true`). Each option is one finding, labeled `<target>: <proposed_change truncated to the first line>`. For each chosen item, state the planned edit, then apply with `Edit` (or `Write` if the file is new).

## Step 6: Render the report

Short. Omit any empty section.

1. **Applied**: one line per Step 4 auto-apply, format: `<target>: <one-line summary>`. Mark failed writes with `(FAILED)`.
2. **Hints**: Agent 2 output, max 3. Format:
   ```
   - <recommendation>. *<rationale>*
   ```
3. **Logged only**: Step 5 overflow findings (never presented to the user) and non-safe findings the user did not pick. Overflow findings are not written to the log in Step 7; only `asked_accepted` and `asked_rejected` entries reflect actual user decisions.

No grading, no congratulations, no narrative session summary.

## Step 7: Log the session

```bash
ls ~/.claude/reflect-logs/.enabled 2>/dev/null && echo "enabled" || echo "skip"
```

If `skip`: stop. The opt-in is handled by `/luca-reflection-kit:luca-reflection-recommended-setup`.

If `enabled`, check Python:

```bash
command -v python3 >/dev/null 2>&1 && echo "ok" || echo "missing"
```

If `missing`: tell the user once ("Session notes couldn't be saved: Python 3 isn't installed.") and stop.

If `ok`: build a single JSON object and pass it to the logger:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/log-session.py" <<'ENTRY'
{"date": "<YYYY-MM-DD>",
 "applied": [{"target": "<path>", "text": "<text>"}, ...],
 "asked_accepted": [{"target": "<path>", "text": "<text>"}, ...],
 "asked_rejected": [{"target": "<path>", "text": "<text>"}, ...],
 "hints": ["<recommendation>", ...]}
ENTRY
```

Use standard JSON escaping.

## Where the data lives

- Session log: `~/.claude/reflect-logs/<project-slug>.jsonl`, one line per session.
- Toggle session notes: `/luca-reflection-kit:luca-reflection-recommended-setup`.
- View notes: `cat ~/.claude/reflect-logs/<project>.jsonl`
- Delete notes: `rm ~/.claude/reflect-logs/<project>.jsonl`
