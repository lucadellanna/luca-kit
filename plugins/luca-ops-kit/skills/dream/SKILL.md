---
name: dream
description: >
  Use this skill when the user says "dream", "/dream", or asks to surface
  cross-session patterns, consolidate memory, or review what /reflect has
  learned across multiple sessions. Mines /reflect session logs to find
  recurring suggestions never acted on, memory contradictions, and patterns
  invisible within a single session.
version: 0.1.0
---

# Dream

Mine /reflect session logs to surface patterns only visible across multiple sessions. Identifies recurring suggestions never acted on, memory contradictions, skill drift, and cross-project signals.

## Step 1: Scope and load

If not specified in the opening message, ask using AskUserQuestion:

- **Scope**: current project (default) or all projects?
- **Date range**: how far back? (default: 90 days)
- **Options**: dry run (show findings only, no writes)?
- **Focus**: any specific area to prioritize? (optional, e.g., "errors only", "skill improvements")

**Derive current repo slug** using the same method as /reflect Step 5b (git remote → `org__repo`, fallback to dir name, fallback to `no-repo`).

**Load logs:**

For single project:
```bash
cat ~/.claude/reflect-logs/<slug>.jsonl
```
Filter to entries within the date range using Python or `jq`.

For `all` projects: pre-aggregate via Bash before loading into context (raw multi-repo logs overflow context). Substitute the number of days from the user's date range for `DAYS` (default: 90):
```bash
SINCE=$(python3 -c "import datetime; print((datetime.date.today() - datetime.timedelta(days=DAYS)).isoformat())")

# Top recurring finding texts with source repo
jq -rn --arg since "$SINCE" \
  'inputs as $e | select($e.date >= $since) | $e.findings[] |
  [(input_filename | split("/")[-1] | rtrimstr(".jsonl")), .text] | @tsv' \
  ~/.claude/reflect-logs/*.jsonl 2>/dev/null \
  | sort | uniq -c | sort -rn | head -50

# Skill improvement targets with source repo
jq -rn --arg since "$SINCE" \
  'inputs as $e | select($e.date >= $since) | $e.findings[] | select(.type=="skill_improvement") |
  [(input_filename | split("/")[-1] | rtrimstr(".jsonl")), .skill] | @tsv' \
  ~/.claude/reflect-logs/*.jsonl 2>/dev/null \
  | sort | uniq -c | sort -rn

# Memory targets with source repo (contradiction candidates)
jq -rn --arg since "$SINCE" \
  'inputs as $e | select($e.date >= $since) | $e.findings[] | select(.type=="memory") |
  [(input_filename | split("/")[-1] | rtrimstr(".jsonl")), .memory_target] | @tsv' \
  ~/.claude/reflect-logs/*.jsonl 2>/dev/null \
  | sort | uniq -c | sort -rn | awk '$1 > 1'
```
Load full entries only for repos where pre-aggregation shows signal (≥2 matching findings, covering the lowest Step 2 detection threshold). Skip entries with unknown `schema` values; report a count of skipped entries if any.

**Load memory files:**
- Project memory: `<repo-root>/.claude/memory/*.md`
- Global memory: `~/.claude/MEMORY.md`

**Load code-review checklist** (if it exists):
```bash
cat ~/.claude/code-review-checklist.md 2>/dev/null
```

If no log file found for the current project: "No session notes found for this project. Run /reflect at least once with session notes enabled; it will ask on the next run."

## Step 2: Mine cross-session signal

Analyze entries within the date window and identify:

| Signal | Detection rule | Priority |
|--------|---------------|----------|
| Recurring suggestion, never acted on | Same `finding_id`-equivalent finding (matched by `type` + `text`) appears in ≥3 entries; in those sessions, no `actions_taken` entry has a `finding_id` referencing that finding | High |
| Memory contradiction | Same `memory_target` field in entry A and later entry B with conflicting `text`; current memory file still has A's version | High |
| Action not sticking | Same finding text in ≥3 entries AND matching `actions_taken` present each time; the action isn't solving the root cause | High |
| Skill drift | Same `skill` value in ≥3 entries with inconsistent `change` summaries | Medium |
| Stale insight | Finding not seen in last 10 entries but referenced in current memory file | Medium |
| Cross-project pattern (`all` mode only) | Same `text` or `category` appearing in ≥2 repos | High (CLAUDE.md candidate) |
| Stale checklist item | Item in `~/.claude/code-review-checklist.md` has no semantically matching finding across all sessions in the date window | Medium |
| Duplicate checklist items | Two checklist items describe overlapping patterns (judge semantically, not by exact text) | Medium |

## Step 3: Score

Spawn a Haiku sub-agent to score the findings. Pass it:
1. The full findings list
2. These criteria and their definitions
3. The instruction: "Score each criterion 0–10. For each, give a one-sentence rationale. Return a markdown table."

Criteria:
1. **Precision**: each finding is scoped correctly: not too broad, not a single-session detail
2. **Non-triviality**: no observations that apply to any set of sessions
3. **Concreteness**: every actionable finding names a specific next step
4. **Coverage**: no obvious cross-session patterns were missed
5. **Accuracy**: each finding is grounded in the actual log data, not inferred beyond what it contains

If average < 9.5, revise and re-score. Stop after 3 iterations or if score stops improving (< 0.5 gain counts as stagnant; one extra iteration allowed if prior changes were substantive). Do not present findings until threshold met or iterations exhausted.

## Step 4: Present and act

If `--dry-run`: present findings only, then stop. No writes.

Otherwise, present findings grouped by action type. Omit empty categories. Mark each **High** or **Medium**.

AskUserQuestion (multiSelect: true) with the specific items as options:
- **Memory updates**: update or remove the stale/contradicted entry
- **Skill improvements**: apply a consolidated fix resolving drift or recurring gap
- **CLAUDE.md additions** (`all` mode only): elevate cross-project pattern
- **Checklist maintenance**: remove stale items, merge duplicates, reword overly-specific entries (show proposed diff before writing)
- **No action needed**: note only

Apply chosen actions. One focused edit per finding. For memory updates and checklist edits, show the exact proposed change before writing.

## Step 5: Self-reflection

Spawn a Haiku sub-agent to verify:

1. **Impact**: at least one action applied. Auto-pass if user declined all or only insights surfaced.
2. **Quality**: Step 3 gate passed (avg ≥ 9.5 or all 3 iterations completed).
3. **No overreach**: only selected actions were taken.
4. **Log integrity**: no `.jsonl` file was modified by this run.

If any criterion scores below 8, draft a concise edit to this SKILL.md, show it to the user, and apply on approval.

## Design decisions

| Decision | Rationale |
|----------|-----------|
| /dream never writes to .jsonl logs | Logs are append-only; only /reflect writes. Prevents dream contaminating its own input corpus. |
| Scope defaults to current repo | Least-surprise default; `all` requires explicit opt-in. |
| `all` mode pre-aggregates via jq | Raw multi-repo logs overflow model context; jq extracts only threshold-meeting candidates before the model sees them. |
| 90-day default window | Balances recency with capturing never-acted-on patterns that may be older. |
| `--dry-run` flag | Builds user trust before any writes; recommended for first run. |
| `memory_target` for contradiction detection | Structured field lookup is reliable; free-text NLP comparison is not. |
| Reads `<repo>/.claude/memory/` not `~/.claude/projects/*/memory/` | The latter is Conductor's auto-memory and is wiped on workspace rotation. |
| Scoring criteria duplicated from /reflect Step 3 | Intentional: skills must be self-contained; cross-skill references to prose sections break if the source skill is renamed or restructured. |
| Checklist pruning in /dream, not /review-loop | /review-loop only has single-session visibility; /dream has the cross-session data needed to judge whether an item is genuinely stale vs. just not triggered recently. |
