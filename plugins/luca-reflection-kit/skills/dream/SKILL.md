---
name: dream
description: >
  Use this skill when the user says "dream", "/dream", or asks to surface
  cross-session patterns, prune the rule corpus, or review what /reflect
  has accumulated across sessions. Mines reflect logs and optional sources
  (error log, code-review checklist) for patterns visible only across
  sessions, proposes a small ranked list of pruning or consolidation
  actions, and applies only what the user confirms.
version: 0.2.0
---

# Dream

Cross-session pruning orchestrator. Loads multi-session signals, runs deterministic detections, decides on a specific action per candidate, asks the user which to apply, applies them, logs the run for future suppression.

You are the orchestrator and the analyst. There are no sub-agents. Detections run in Bash/Python. The translation from candidate to action is your inline reasoning.

## Step 1: Locate the reflect log

Derive the project slug the same way the logger does:

```bash
ORIGIN=$(git remote get-url origin 2>/dev/null)
if [ -n "$ORIGIN" ]; then
  CLEAN=$(echo "$ORIGIN" | sed 's:/$::; s:\.git$::')
  SLUG=$(echo "$CLEAN" | tr ':' '/' | awk -F/ '{print $(NF-1) "__" $NF}')
else
  TOP=$(git rev-parse --show-toplevel 2>/dev/null)
  SLUG=$(basename "$TOP" 2>/dev/null || echo "no-repo")
fi
SLUG=$(echo "$SLUG" | sed 's/[^A-Za-z0-9_-]/-/g')
LOG="$HOME/.claude/reflect-logs/${SLUG}.jsonl"
```

If `$LOG` does not exist, output one line: "No reflect log for this project : run /reflect at least once with session notes enabled." and stop.

## Step 2: Pre-flight on log size

```bash
COUNT=$(wc -l < "$LOG")
SIZE=$(wc -c < "$LOG")
```

If `COUNT > 200` OR `SIZE > 5242880` (5 MB), ask via `AskUserQuestion`:

- Process all entries
- Last 90 days (default)
- Last 30 days
- Custom range

Below the threshold, process all entries silently. Set `SINCE` accordingly (`1970-01-01` for "all").

## Step 3: Normalize entries

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/migrate-log.py" "$LOG" "$SINCE"
```

The script emits a JSON array of records, each shaped `{date, applied, asked_accepted, asked_rejected, hints, historical}`. Schemas 1, 2, and 3 are normalized; unknown schemas are silently skipped. Hold the array in working memory.

## Step 4: Load rule corpus and optional sources

```bash
cat .claude/memory/MEMORY.md 2>/dev/null
cat CLAUDE.md 2>/dev/null
cat ~/.claude/CLAUDE.md 2>/dev/null
cat ~/.claude/MEMORY.md 2>/dev/null
cat "${CLAUDE_PLUGIN_ROOT}/CLAUDE.md" 2>/dev/null
test -f ~/.claude/error-log.md && cat ~/.claude/error-log.md
test -f ~/.claude/code-review-checklist.md && cat ~/.claude/code-review-checklist.md
```

Hold each output separately in working memory. Optional sources skipped silently if absent.

Check qmd availability:

```bash
if test -f ~/.claude/luca-kit/reflection-context-search-configured; then echo marker_present; else echo marker_absent; fi
```

Store as `$QMD_AVAILABLE` (same two-condition check: marker present AND `mcp__qmd__query` in this session's available-tools list).

## Step 5: Run deterministic detections

Produce candidates. A candidate is `{key, pattern, evidence}` where `key` is a stable identifier (a short slug derived from the pattern + target), `pattern` is a one-sentence description, `evidence` is the entries that triggered the detection.

### From reflect logs (always)

1. **Recurring concept**: aggregate all text from `applied + asked_accepted + asked_rejected + hints + historical` across records, whitespace-normalize, count by text. Texts with count ≥ 3 emit a candidate.
2. **Repeated rejection**: a text with ≥ 2 occurrences in `asked_rejected` and 0 in `applied + asked_accepted` emits a candidate.
3. **Recurrence after write**: for each `(target, text)` in any `applied` or `asked_accepted` entry on date D, search records after D for the same normalized text in any field. A match emits a candidate.
4. **Memory contradiction**: group `applied` entries with a memory file target by their `**Topic**:` prefix. Two entries sharing a prefix but differing in the text after it emit a candidate.
5. **Skill drift**: group `applied` and `asked_accepted` entries with a skill file target. If a target has ≥ 3 entries with pairwise-different text, emit a candidate.

### From error log (only if loaded)

6. **Recurring error class**: parse error-class names from the error log. ≥ 3 occurrences within the window emit a candidate.
7. **Structural-proposed unaged**: each error-log entry with file `structural-proposed` older than 14 days, with no matching rule update in the rule corpus, emits a candidate.

### From checklist (only if loaded)

Deterministic detection of stale or duplicate checklist items is too brittle. Pass all checklist items as raw input to Step 7; the analysis step judges them.

## Step 6: Suppress previously-rejected candidates

If `~/.claude/dream-logs/${SLUG}.jsonl` exists, read it. Each line is `{date, candidates: [{key, outcome, ...}]}`.

For each candidate from Step 5: if its `key` appears in a past dream log entry with `outcome: rejected`, and no normalized record from Step 3 dated after that rejection mentions the same concept (text match in any field), drop the candidate.

## Step 7: Analyze inline

Examine the surviving candidates and the rule corpus. If `$QMD_AVAILABLE`, for each candidate run a targeted semantic search before composing the action:

```
mcp__qmd__query with searches=[{type:"vec", query:"<candidate pattern text>"}], intent="existing rule, skill, or memory entry covering this concept"
```

Include results with score ≥ 0.6 as supplementary evidence. If a high-scoring result shows the concept is already fully captured, adjust the action from `escalate` to `drop` or from `rewrite` to `merge` with the existing content.

For each candidate (or near-duplicate cluster):

- Choose an action: `delete`, `rewrite`, `merge`, `escalate` (project rule → global rule), or `drop` (your judgment: not actually a problem).
- Compose the exact text the action will produce (target file path + new content, or the line to delete).
- Estimate impact: `high`, `medium`, or `low`, based on recurrence count and severity.

For raw checklist input (Step 5, third group), judge each item: stale (no matching reflect-log finding) → propose `delete`; duplicate (overlaps another item) → propose `merge` with the exact merged text.

## Step 8: Render and ask

Drop candidates with action `drop` entirely. Rank the rest by impact. Cap displayed at 7. Render as a numbered list:

```
1. <pattern>
   Evidence: <one-line summary of triggering entries>
   Proposed action: <verb> in <target>: <exact text>

2. ...
```

Ask:

> Reply with the numbers to apply (e.g., `1 2 4`), `all`, `none`, or a range (`1-3`).

Parse: space-separated integers, the literal words `all` or `none`, or hyphenated ranges (inclusive). On invalid input (non-numeric tokens or out-of-range indices), surface the offending tokens and re-ask once. After one re-ask, treat unknown input as `none`.

## Step 9: Apply

For each chosen candidate, in display order:

1. State the planned edit in one line.
2. Apply with `Edit` or `Write`.
3. Record outcome for Step 10.

If a write fails, surface the failure and continue with the rest.

## Step 10: Log

```bash
mkdir -p ~/.claude/dream-logs
```

Append one JSONL line to `~/.claude/dream-logs/${SLUG}.jsonl`:

```json
{
  "schema": 1,
  "date": "<YYYY-MM-DD>",
  "candidates": [
    {"key": "<key>", "pattern": "<one sentence>", "proposed_action": "<verb> in <target>", "outcome": "applied"},
    {"key": "...", "pattern": "...", "proposed_action": "...", "outcome": "rejected"}
  ]
}
```

Every candidate displayed in Step 8 is logged. Picked → `applied`. Not picked (or rejected via `none`) → `rejected`. The next /dream run uses these in Step 6 for suppression.

## Where the data lives

- Reflect logs (input): `~/.claude/reflect-logs/<slug>.jsonl`: written by /reflect, read by /dream.
- Dream logs (own state): `~/.claude/dream-logs/<slug>.jsonl`: written by /dream only.
- View dream history: `cat ~/.claude/dream-logs/<slug>.jsonl`
- Reset dream suppression: `rm ~/.claude/dream-logs/<slug>.jsonl`
