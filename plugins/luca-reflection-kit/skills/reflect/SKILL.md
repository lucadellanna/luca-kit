---
name: reflect
description: >
  Use this skill when the user says "reflect", "let's reflect", or asks to
  analyze the current conversation for learning points, errors, and improvement
  opportunities. Orchestrates two specialist reviewers (Claude-side and
  user-side) over a verbatim conversation digest, synthesizes their findings
  into a prioritized report with evidence, auto-applies clear low-risk wins
  to project memory, and asks before any other change.
version: 0.5.5
---

# Reflect

Orchestrator. Assembles a conversation digest, spawns two specialist sub-agents in parallel, synthesizes their findings, renders a report with evidence, auto-applies gated wins, asks about the rest, and logs the session.

You are not the reviewer. The reviewers are sub-agents. Your job is to gather evidence, route it, and synthesize. Stay neutral when building the digest.

## Step 0: Length check

If fewer than ~5 substantive exchanges since the last `/reflect` (or session start if none), say "Not enough material to reflect on meaningfully" and stop.

Do not mention session-note opt-in here. The setup command handles that separately.

## Step 1: Gather inputs

### 1a. Build the conversation digest

Construct a verbatim digest of conversation turns since the last `/reflect` (or session start). Each turn is kept as-is. Format:

```
--- Turn N ---
[user]
<verbatim user message>

[claude tool: <tool-name>(<args summary>)]
<tool output, truncated: keep first 5 + last 5 lines, mark "[... K lines omitted ...]" in between if longer>

[claude]
<verbatim Claude response text>
```

Rules:
- No interpretation. No labels like "error" or "pushback". Just enumerate turns.
- Truncate tool outputs aggressively (5 + 5 lines). Code blocks and file contents inside responses are kept as-is.
- If a turn is trivial (one-word ack), include it briefly; do not skip.

### 1b. Read the rule corpus

The reviewers have `tools: []` and cannot read files themselves. Assemble the full rule corpus so they can detect functional duplicates (not just literal MEMORY.md matches):

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

### 1c. Enumerate available skills and commands

So reviewers can suggest "invoke skill X" or "run command Y" as alternatives to "add memory entry":

```bash
python3 << 'PYEOF'
import os, glob

def parse_fm(path):
    try:
        with open(path) as f: s = f.read(4000)
    except: return None, None
    if not s.startswith("---"): return None, None
    end = s.find("---", 3)
    if end < 0: return None, None
    fm = s[3:end]
    name = desc = ""
    lines = fm.split("\n")
    i = 0
    while i < len(lines):
        stripped = lines[i].strip()
        if stripped.startswith("name:"):
            name = stripped[5:].strip().strip('"\'')
        elif stripped.startswith("description:"):
            val = stripped[12:].strip().strip('"\'')
            if val in ('>', '|', '>-', '|-'):
                block = []
                i += 1
                while i < len(lines) and (lines[i].startswith("  ") or lines[i].startswith("\t")):
                    block.append(lines[i].strip())
                    i += 1
                desc = " ".join(block)
                continue
            else:
                desc = val
        i += 1
    return name, desc[:140].replace("\n", " ")

skill_paths = (
    glob.glob(os.path.expanduser("~/.claude/plugins/cache/*/*/*/skills/*/SKILL.md"))
    + glob.glob(os.path.expanduser("~/.claude/skills/*/SKILL.md"))
    + glob.glob(".claude/skills/*/SKILL.md")
)
cmd_paths = (
    glob.glob(os.path.expanduser("~/.claude/plugins/cache/*/*/*/commands/*.md"))
    + glob.glob(os.path.expanduser("~/.claude/commands/*.md"))
    + glob.glob(".claude/commands/*.md")
)

print("=== SKILLS AVAILABLE ===")
for p in sorted(set(skill_paths)):
    n, d = parse_fm(p)
    if n: print(f"- {n}: {d}")

print()
print("=== COMMANDS AVAILABLE ===")
for p in sorted(set(cmd_paths)):
    n, d = parse_fm(p)
    if not n:
        n = os.path.basename(p)[:-3]
    print(f"- {n}: {d}")
PYEOF
```

Hold the digest, rule corpus, and skills/commands index in working memory for Step 2.

## Step 2: Spawn the two reviewers in parallel

Send a single message with two `Agent` tool calls (parallel execution):

- `subagent_type: "luca-reflection-kit:claude-flow-reviewer"`
- `subagent_type: "luca-reflection-kit:user-flow-reviewer"`

The two reviewers have asymmetric outputs:

- **claude-flow-reviewer** produces findings (target file + proposed change) destined for the auto-apply gate or the user's AskUserQuestion.
- **user-flow-reviewer** produces recommendations classified as automatable (includes proposed_rule + target, routed into the claude-flow pipeline) or user-only (rendered as Hint, max 3). It does not directly apply edits.

Both calls share the first three inputs:

1. The full digest from Step 1a.
2. The full rule corpus from Step 1b (project MEMORY.md + global CLAUDE.md + project CLAUDE.md + plugin runtime CLAUDE.md). The reviewer uses this to detect functional duplicates: a finding/observation already enforced by an existing rule is dropped.
3. The skills + commands index from Step 1c. Reviewers can suggest "invoke skill X" or "run command Y" instead of encoding a new rule.

**claude-flow-reviewer also receives** the auto-apply gate criteria, verbatim:

```
AUTO-APPLY GATE: A finding qualifies for `disposition: apply` only if ALL of:
- target is `.claude/memory/MEMORY.md` (project memory; never CLAUDE.md, never any skill file, never any other plugin file)
- confidence is high
- proposed text is ≤2 lines
- not a functional duplicate of any rule in the rule corpus above (literal text match OR same behavior already enforced by a different phrasing)
- the proposed text changes future behavior beyond what existing rules / skills / commands already enforce (the value-adding test)

Any finding failing any criterion uses `disposition: review` (orchestrator will ask the user) or `disposition: ignore`.
```

**Reminders (one per reviewer):**

- claude-flow: "Return findings in the format specified in your system prompt. Cite verbatim evidence. Run every finding through the quality floor (value-adding test included). Findings may include 'user has restated requirement X N times; add to MEMORY.md'. That is a Claude-side memory change and belongs to you, not to user-flow-reviewer."
- user-flow: "Return recommendations in the format specified in your system prompt. Cite verbatim evidence. No coaching tone. For automatable recommendations, include proposed_rule and target fields; do not directly apply any edits."

## Step 3: Synthesize

Treat the two reviewers' outputs as follows:

- **claude-flow findings** go through the auto-apply gate (Step 4), the rendering pipeline (Step 5), and the AskUserQuestion path (Step 6).
- **user-flow recommendations** are split by their `automatable` field:
  - `automatable: yes` → convert each into a claude-flow finding using the agent's `proposed_rule` and `target`. Assign `confidence: medium` and `disposition: review` as defaults (the gate in Step 4 may upgrade `disposition` to `apply`). Add to the claude-flow set and synthesize together.
  - `automatable: no` → set aside as user-only hints. Cap at 3 by likely impact (1 or 2 is acceptable). Render under "Hint(s)" in Step 5. No gate, no AskUserQuestion.

**Both empty (`None.`)**: tell the user "Both reviewers found nothing worth surfacing." Skip Steps 4–6 and proceed to Step 7 for logging.

**One reviewer returned `None.`**: proceed with the other's output. Add a one-line warning at the top of the report: "Note: <reviewer-name> returned no findings."

**Synthesis rules for claude-flow findings only:**

- **Deduplicate within claude-flow output**: two findings are duplicates if they share target file AND propose substantively similar text. Keep the higher-confidence one.
- **Source-tree dedup (fallback).** Reviewers receive the full rule corpus in Step 1b, so they should self-filter functional duplicates. As defense in depth, before keeping any finding whose target is a skill, agent, command, or CLAUDE.md file modified in this session, Read the current content of that file and reject the finding if the proposed change is already implemented. This catches edge cases where a file changed in the session but the reviewer's view of "what's encoded" is stale.
- **Reject weak items**: drop findings with `confidence: low` AND `disposition: review`. They are noise.
- **Rank**: order by confidence (high first), then by specificity of target.

## Step 4: Auto-apply gated items

For each finding with `disposition: apply` that meets the gate:

1. Grep `.claude/memory/MEMORY.md` and the project CLAUDE.md for the proposed text. If a match exists, skip and move the finding to `review` disposition.
2. Append the proposed text to `.claude/memory/MEMORY.md` under the appropriate section (`## Preferences`, `## Context`; create file/section if absent). Use Edit or Write.
3. Note in working memory whether the write succeeded.

If any auto-apply write fails, do not silently move on: record the failure and surface it in the report.

## Step 5: Render the report

Sections, in order. Omit any empty section.

1. **Warnings** (only if a reviewer returned `None.` or an auto-apply write failed).
2. **Top recommended next actions** (max 3 from claude-flow findings, ranked by confidence × specificity). User-flow recommendations are surfaced in their own section, not bundled here.
3. **Claude-side improvements** (claude-flow non-applied findings, using the finding schema below).
4. **Hint(s)** (user-only recommendations from user-flow, max 3). Format spec below.
5. **Auto-applied** (what was written in Step 4, with file path and exact text).
6. **Logged only** (claude-flow items with disposition: review that propose no change).

**Finding schema** (claude-flow):

```
- **Evidence**: "<verbatim quote>"
- **Observation**: <one sentence>
- **Proposed change**: <one sentence>
- **Target**: <file path>
- **Confidence**: high | medium | low
```

**Hint(s) format** (user-flow `automatable: no` items, max 3):

```
**Hint(s):**
- <recommendation sentence in normal text>. *<rationale sentence in italic.>*
- ...
```

Plain language. No jargon. The recommendation is what to try next time; the rationale is the one-sentence reason it would help. If only 1 or 2 user-only items survive the cap, that is fine.

## Step 6: Ask the user about non-applied claude-flow findings

Only claude-flow findings have an "apply" path. User-flow observations are informational and never asked about.

Collect all claude-flow findings with `disposition: review` that propose a change (not just observations). If more than 4, keep the top 4 by confidence; the rest are mentioned at the end of the report as "X more findings logged only". (AskUserQuestion has a hard 4-option limit.)

If the count is zero, skip this step.

Otherwise call AskUserQuestion (multiSelect: true). Each option is one finding, labeled `<target>: <one-line summary>`. The user picks which to apply.

For each chosen item:
- **Memory updates**: write to `.claude/memory/MEMORY.md`. State the exact text before writing.
- **Skill edits**: state the planned edit (one line), then apply with Edit.
- **CLAUDE.md edits**: state the planned edit, confirm scope (project vs global), apply with Edit.
- **New skill**: run `/create-skill` with the proposed name, purpose, and trigger as context.

## Step 7: Log session

Silent opt-in check at the top:

```bash
ls ~/.claude/reflect-logs/.enabled 2>/dev/null && echo "enabled" || echo "skip"
```

- `skip`: stop. No prompt, no nag. The setup command handles opt-in.
- `enabled`: continue.

Check `python3`:

```bash
command -v python3 >/dev/null 2>&1 && echo "ok" || echo "missing"
```

If `missing`: tell the user once: "Session notes couldn't be saved: Python 3 isn't installed. Get it from python.org when ready." Stop.

If `ok`: build a JSON array of finding strings (one string per finding, from both reviewers, regardless of disposition). Then run:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/log-session.py" <<'FINDINGS'
["finding 1", "finding 2"]
FINDINGS
```

Use standard JSON string escaping.

## Where the data lives

Session notes are saved to `~/.claude/reflect-logs/<project-name>.jsonl`, one line per session.

- To change the opt-in: run `/luca-reflection-kit:luca-reflection-recommended-setup`.
- To view notes: `cat ~/.claude/reflect-logs/<project>.jsonl`
- To delete all notes for a project: `rm ~/.claude/reflect-logs/<project>.jsonl`
