---
name: compact-claude-files
description: >
  Shortens your CLAUDE.md, memory files, and path-rule files by applying
  within-file tightenings and sentence-level compressions. Does not move
  content between files; for cross-file reorganization use
  /luca-kit:restructure-claude-files. Applies changes automatically and
  verifies no load-bearing content was lost.
version: 0.1.0
---

# Compact Claude Files

Removes redundant phrasing and shortens verbose content inside each file Claude Code loads automatically: CLAUDE.md, memory files (`.claude/memory/*.md`), and path-rule files (`.claude/rules/*.md`). Within-file edits only; cross-file moves and scope rebalancing live in `/luca-kit:restructure-claude-files`.

Trust model:

- **Reviewers** (read-only) propose changes.
- **Orchestrator** applies them automatically.
- **Verifier** catches accidental loss of important info.
- **User** intervenes only when the verifier flags something the orchestrator cannot resolve with confidence.

## Step 1: Scope and discover files

Ask the user which scope to compact:

> "What would you like to compact?"

Two options: `Project only (CLAUDE.md + memory + rules)`, `Project + global (all files)`.

Then run (pass `project` for project-only scope, `all` for project + global):

```bash
bash "${CLAUDE_PLUGIN_ROOT}/scripts/discover-claude-files.sh" <project|all>
```

If the user selected project-only, exclude all global files from targets. If no files exist within the selected scope, say so and stop.

Label existing files as **targets**. Record the total character count of all targets (sum of `wc -c` outputs) as **chars_before**.

## Step 2: Run reviewers in parallel

Send all Agent calls in a single message. Each reviewer reads the file itself; the orchestrator does not load file contents into main context.

**Per CLAUDE.md target** (each CLAUDE.md that exists within scope):

- `subagent_type: "luca-kit:claude-md-structural-reviewer"`: prompt is the absolute path. Use only `tighten` findings; record any `move` findings for the bridge in Step 5.
- `subagent_type: "luca-kit:claude-md-compression-reviewer"`: prompt is the absolute path.

**Per memory file target and per rule file target**:

- `subagent_type: "luca-kit:claude-md-compression-reviewer"`: prompt is the absolute path.

Each agent's mandate and output format are defined in the agent's own file.

If all reviewers return zero findings (and no move-outs were noted for the bridge), say "Nothing to compact." and stop.

## Step 3: Cache and apply

Cache each target before writing:

```bash
test -f "$PROJECT_CLAUDE" && cp "$PROJECT_CLAUDE" /tmp/compact-claude-files-project-orig.md
test -f "$GLOBAL_CLAUDE"  && cp "$GLOBAL_CLAUDE"  /tmp/compact-claude-files-global-orig.md
```

For each memory or rule file target, hash its absolute path and cache it:

```bash
hash=$(python3 -c "import hashlib,sys; print(hashlib.md5(sys.argv[1].encode()).hexdigest())" "$path")
cp "$path" /tmp/compact-claude-files-aux-$hash.md
```

Track each `<path> -> /tmp/compact-claude-files-aux-<hash>.md` mapping for Step 4.

Apply tightenings and compressions:

| Finding | Action |
|---|---|
| Tightening (CLAUDE.md, type `tighten`) | `Edit`: replace `before` with `after` (empty string if `after` is `(remove)`) |
| Compression (any target) | `Edit`: replace `before` with `after` |
| Move-out (type `move`) | Skip and record for the Step 5 bridge; not handled by this command. |

If any `Edit` fails because the `before` snippet is gone (a prior edit overlapped it), note as skipped and continue.

## Step 4: Verify

Send one Agent call per target that was modified:

- `subagent_type: "luca-kit:claude-md-loss-verifier"`

Prompt: two lines, the cached original path then the current file path.

The verifier returns either `No meaningful content lost.` or a bulleted list of important losses.

## Step 5: Report and react

Show per target (skip a target section if it had no findings):

1. **Applied**: one line per change in plain English (e.g., "Shortened Em dashes bullet", "Merged two DESIGN.md rules"). Include skipped/duplicate notes. Do not use reviewer-internal identifiers (T1, C1, etc.) -- the user has not seen the raw reviewer output.
2. **Verifier result**: verbatim, per modified file.

If all verifiers returned `No meaningful content lost.`: proceed to the compression metric.

If any verifier flagged losses, evaluate each item:

- **Keep removed**: the removal was intentional -- stale content or deliberate simplification. Note inline; no user input needed.
- **Restore**: the loss is clearly accidental -- load-bearing content removed by mistake. Restore immediately without asking.
- **Ambiguous**: you cannot confidently determine whether the loss matters in this project's context.

For **ambiguous** items only: present each with a one-line judgment (why you are unsure) and call `AskUserQuestion` with one option per item plus `All` and `None` (split into multiple questions if the 4-option limit is exceeded). Apply selected restorations. If no items are ambiguous, skip the question.

On any restoration: restore the affected text via inverse `Edit` (re-insert `before`, remove `after`).

Once complete, delete caches:

```bash
rm -f /tmp/compact-claude-files-project-orig.md /tmp/compact-claude-files-global-orig.md /tmp/compact-claude-files-aux-*.md
```

Show the compression metric:

> **Reduction:** X% (integer), where X = round((chars_before - chars_after) / chars_before * 100). One line, all targets combined.

## Step 6: Bridge to restructure

If any `move` findings were recorded in Step 2, end with one line:

> The reviewers also surfaced N items that could move to memory, path rules, skills, or hooks. Run `/luca-kit:restructure-claude-files` to handle them.

Substitute N with the actual count. Skip this step entirely if no move-outs were noted.
