---
name: audit-claude
description: >
  Tightens your project's ./CLAUDE.md, global ~/.claude/CLAUDE.md, and
  co-located memory files by removing redundancy and content that belongs
  elsewhere. Flags cross-type mismatches (CLAUDE.md vs memory, path-rule
  candidates) and scope mismatches between project and global.
  Applies cleanups automatically; asks for input only when the orchestrator
  cannot resolve with confidence.
version: 0.5.0
---

# Audit Claude

Audits CLAUDE.md files and memory files within the selected scope. Removes cruft within each file, proposes cross-type transfers (CLAUDE.md vs memory, path-rule candidates), and flags scope mismatches between project and global.

Trust model:

- **Reviewers** (read-only) propose changes.
- **Orchestrator** applies them automatically.
- **Verifier** catches accidental loss of important info.
- **User** intervenes only when the verifier flags something the orchestrator cannot resolve with confidence.

## Step 1: Scope and discover files

Ask the user which scope to audit:

> "What would you like to audit?"

Two options: `Project only (CLAUDE.md + memory)`, `Project + global (all files)`.

Then run:

```bash
PROJECT_CLAUDE="$(pwd)/CLAUDE.md"
PROJECT_MEM_DIR="$(pwd)/.claude/memory"
GLOBAL_CLAUDE="$HOME/.claude/CLAUDE.md"
GLOBAL_MEM_DIR="$HOME/.claude/memory"

test -f "$PROJECT_CLAUDE" && echo "project CLAUDE.md: $(wc -l < "$PROJECT_CLAUDE") lines, $(wc -c < "$PROJECT_CLAUDE") chars" || echo "project CLAUDE.md: missing"
test -f "$GLOBAL_CLAUDE" && echo "global CLAUDE.md: $(wc -l < "$GLOBAL_CLAUDE") lines, $(wc -c < "$GLOBAL_CLAUDE") chars" || echo "global CLAUDE.md: missing"
find "$PROJECT_MEM_DIR" -maxdepth 1 -name '*.md' 2>/dev/null | while IFS= read -r f; do echo "project memory: $f ($(wc -l < "$f") lines, $(wc -c < "$f") chars)"; done
find "$GLOBAL_MEM_DIR" -maxdepth 1 -name '*.md' 2>/dev/null | while IFS= read -r f; do echo "global memory: $f ($(wc -l < "$f") lines, $(wc -c < "$f") chars)"; done
```

If the user selected project-only, exclude all global files from targets. If no files exist within the selected scope, say so and stop.

Label existing files as **targets**. Record the total character count of all targets (sum of `wc -c` outputs) as **chars_before** for the compression metric.

## Step 2: Run reviewers in parallel

Send all Agent calls in a single message. Each reviewer reads the file itself; the orchestrator does not load file contents into main context.

**Per CLAUDE.md target** (each CLAUDE.md that exists within scope):

- `subagent_type: "luca-kit:claude-md-structural-reviewer"`: prompt is the absolute path.
- `subagent_type: "luca-kit:claude-md-compression-reviewer"`: prompt is the absolute path.

**Per memory file target** (each `.md` file in the memory dirs within scope):

- `subagent_type: "luca-kit:claude-md-compression-reviewer"`: prompt is the absolute path.

**If both project and global CLAUDE.md exist within scope**:

- `subagent_type: "luca-kit:claude-md-scope-reviewer"`: prompt is two lines, the project CLAUDE.md path then the global CLAUDE.md path.

**Always** (when any targets were discovered):

- `subagent_type: "luca-kit:claude-md-cross-reviewer"`: prompt lists all discovered file paths, one per line, each prefixed by type: `CLAUDE.md: <path>` or `memory: <path>`.

The cross-reviewer returns memory-to-CLAUDE.md candidates and path-rule candidates (all advice-only).

Each agent's mandate, finding categories, and output format are defined in the agent's own file.

If all reviewers return zero findings, say "Nothing to surface." and stop.

## Step 3: Cache and apply

Cache each target before writing:

```bash
test -f "$PROJECT_CLAUDE" && cp "$PROJECT_CLAUDE" /tmp/audit-claude-project-orig.md
test -f "$GLOBAL_CLAUDE"  && cp "$GLOBAL_CLAUDE"  /tmp/audit-claude-global-orig.md
```

For each memory file target, compute a hash of its absolute path and cache it:

```bash
hash=$(python3 -c "import hashlib,sys; print(hashlib.md5(sys.argv[1].encode()).hexdigest())" "$path")
cp "$path" /tmp/audit-claude-mem-$hash.md
```

Track each `<path> -> /tmp/audit-claude-mem-<hash>.md` mapping for Step 4.

Apply structural and compression findings without asking the user. Routing:

| Finding | Action |
|---|---|
| Tightening (CLAUDE.md) | `Edit`: replace `before` with `after` (empty string if `after` is `(remove)`) |
| Compression (CLAUDE.md or memory file) | `Edit`: replace `before` with `after` |
| Move-out to co-located memory dir | (1) Check if snippet already exists in target; skip if duplicate. (2) Append with a leading newline (create if absent). (3) If the memory directory has an index file (MEMORY.md), add a one-line entry in the format `**topic**: one-line summary` where topic is the content's subject (not the filename) and summary is the content distilled to one line, matching the style of existing entries. (4) Edit: remove from CLAUDE.md. |
| Move-out, any other target | Carry forward to Step 5 as advice. |
| Cross-reviewer finding | Carry forward to Step 5 as advice. |
| Scope-transfer finding | Carry forward to Step 5 as advice. |

**Co-located memory directories:** for `./CLAUDE.md` that is `./.claude/memory/`; for `~/.claude/CLAUDE.md` that is `~/.claude/memory/`.

If any `Edit` fails because the `before` snippet is gone (a prior edit overlapped it), note as skipped and continue.

## Step 4: Verify

Send one Agent call per target that was modified:

- `subagent_type: "luca-kit:claude-md-loss-verifier"`

Prompt: two lines, the cached original path then the current file path. For CLAUDE.md files: `/tmp/audit-claude-project-orig.md` and the project path; `/tmp/audit-claude-global-orig.md` and the global path. For memory files: `/tmp/audit-claude-mem-<hash>.md` and the memory file path.

The verifier returns either `No meaningful content lost.` or a bulleted list of important losses.

## Step 5: Report and react

Show per target (skip a target section if it had no findings):

1. **Applied** (project CLAUDE.md / global CLAUDE.md / memory files): one line per change. Include skipped/duplicate notes.
2. **Advice**: non-memory move-outs, cross-reviewer findings (memory-to-CLAUDE.md candidates, path-rule suggestions), scope-transfer recommendations. Empty section omitted.
3. **Verifier result**: verbatim, per modified file.

If all verifiers returned `No meaningful content lost.`: proceed to compression metric.

If any verifier flagged losses, evaluate each item:

- **Keep removed**: the removal was intentional -- stale content, deliberate simplification, or content moved to memory. Note inline; no user input needed.
- **Restore**: the loss is clearly accidental -- load-bearing content removed by mistake. Restore immediately without asking.
- **Ambiguous**: you cannot confidently determine whether the loss matters in this project's context.

For **ambiguous** items only: present each with a one-line judgment (why you are unsure) and call `AskUserQuestion` with one option per item plus `All` and `None` (split into multiple questions if the 4-option limit is exceeded). Apply selected restorations. If no items are ambiguous, skip the question.

On any restoration: restore the affected text via inverse `Edit` (re-insert `before`, remove `after`). For memory move-outs, also remove the appended snippet from the memory file and its corresponding entry from MEMORY.md (best effort).

Once complete, delete caches and show the compression metric:

```bash
rm -f /tmp/audit-claude-project-orig.md /tmp/audit-claude-global-orig.md /tmp/audit-claude-mem-*.md
```

Measure the final character count (`wc -c`) of each modified target. Compute total chars before (recorded in Step 1) and after (sum of current counts). Show:

> **Reduction:** X% (integer), where X = round((chars_before - chars_after) / chars_before * 100). One line, all targets combined.
