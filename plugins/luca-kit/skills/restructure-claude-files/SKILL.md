---
name: restructure-claude-files
description: >
  Reorganizes content across the files Claude Code loads automatically:
  moves content out of CLAUDE.md to co-located memory, surfaces cross-type
  transfer candidates (memory entries that should become CLAUDE.md rules,
  path-rule extractions), and flags scope mismatches between project and
  global CLAUDE.md. Memory move-outs apply automatically; other findings
  are surfaced as advice. For within-file shortening use
  /luca-kit:compact-claude-files.
version: 0.1.0
---

# Restructure Claude Files

Moves content between the files Claude Code loads automatically: CLAUDE.md, memory files (`.claude/memory/*.md`), and path-rule files (`.claude/rules/*.md`). Memory move-outs apply automatically; non-memory destinations, cross-type promotions, and project ↔ global rebalancing surface as advice. For within-file compaction use `/luca-kit:compact-claude-files`.

Trust model:

- **Reviewers** (read-only) propose changes.
- **Orchestrator** applies memory move-outs automatically; everything else is advice.
- **Verifier** catches accidental loss of important info.
- **User** intervenes only when the verifier flags something the orchestrator cannot resolve with confidence.

## Step 1: Scope and discover files

Ask the user which scope to restructure:

> "What would you like to restructure?"

Two options: `Project only (CLAUDE.md + memory + rules)`, `Project + global (all files)`.

Then run (pass `project` for project-only scope, `all` for project + global):

```bash
bash "${CLAUDE_PLUGIN_ROOT}/scripts/discover-claude-files.sh" <project|all>
```

If the user selected project-only, exclude all global files from targets. If no files exist within the selected scope, say so and stop.

Label existing files as **targets**.

## Step 2: Run reviewers in parallel

Send all Agent calls in a single message. Each reviewer reads the file itself; the orchestrator does not load file contents into main context.

**Per CLAUDE.md target** (each CLAUDE.md that exists within scope):

- `subagent_type: "luca-kit:claude-md-structural-reviewer"`: prompt is the absolute path. Use only `move` findings; record any `tighten` findings for the bridge in Step 6.

**If both project and global CLAUDE.md exist within scope**:

- `subagent_type: "luca-kit:claude-md-scope-reviewer"`: prompt is two lines, the project CLAUDE.md path then the global CLAUDE.md path.

**Always** (when any targets were discovered):

- `subagent_type: "luca-kit:claude-md-cross-reviewer"`: prompt lists all discovered file paths, one per line, each prefixed by type: `CLAUDE.md: <path>`, `memory: <path>`, or `rule: <path>`.

Each agent's mandate and output format are defined in the agent's own file.

If all reviewers return zero findings (and no tightenings were noted for the bridge), say "Nothing to restructure." and stop.

## Step 3: Cache and apply

Cache each CLAUDE.md target before writing:

```bash
test -f "$(pwd)/CLAUDE.md"       && cp "$(pwd)/CLAUDE.md"       /tmp/restructure-claude-files-project-orig.md
test -f "$HOME/.claude/CLAUDE.md" && cp "$HOME/.claude/CLAUDE.md" /tmp/restructure-claude-files-global-orig.md
```

Apply move-outs whose suggested target is a memory file in the co-located memory directory. Routing:

| Finding | Action |
|---|---|
| Move-out to co-located memory dir | (1) Check if snippet already exists in target; skip if duplicate. (2) **If target IS MEMORY.md**: append a one-line `**topic**: summary` entry (no separate file). **If target is a separate file**: append the snippet with a leading newline (create if absent), then if the memory directory has a MEMORY.md index, add a one-line entry in the format `**topic**: [summary](relative-path-to-file)` linking to the file. (3) Edit: remove from CLAUDE.md. |
| Move-out, any other target (path rule, skill, hook, template) | Carry forward to Step 5 as advice. |
| Cross-reviewer finding (memory-to-CLAUDE.md, path-rule candidate) | Carry forward to Step 5 as advice. |
| Scope-transfer finding (promote, demote, duplicate) | Carry forward to Step 5 as advice. |

**Co-located memory directories:** for `./CLAUDE.md` that is `./.claude/memory/`; for `~/.claude/CLAUDE.md` that is `~/.claude/memory/`.

If any `Edit` fails because the `before` snippet is gone, note as skipped and continue.

## Step 4: Verify

Send one Agent call per CLAUDE.md target that was modified:

- `subagent_type: "luca-kit:claude-md-loss-verifier"`

Prompt: two lines, the cached original path then the current file path.

The verifier returns either `No meaningful content lost.` or a bulleted list of important losses.

## Step 5: Report and react

Show per target (skip a target section if it had no findings):

1. **Applied**: one line per change in plain English (e.g., "Moved Authoring notes section to .claude/memory/authoring-notes.md"). Include skipped/duplicate notes. Do not use reviewer-internal identifiers (M1, S1, etc.) -- the user has not seen the raw reviewer output.
2. **Advice**: non-memory move-outs (snippet + suggested destination), cross-reviewer findings (memory-to-CLAUDE.md candidates, path-rule suggestions), scope-transfer recommendations (promote, demote, duplicate). Empty section omitted.
3. **Verifier result**: verbatim, per modified file.

If all verifiers returned `No meaningful content lost.`: proceed to Step 6.

If any verifier flagged losses, evaluate each item:

- **Keep removed**: the removal was intentional -- content was moved to memory by design. Note inline; no user input needed.
- **Restore**: the loss is clearly accidental -- load-bearing content removed by mistake. Restore immediately without asking.
- **Ambiguous**: you cannot confidently determine whether the loss matters in this project's context.

For **ambiguous** items only: present each with a one-line judgment and call `AskUserQuestion` with one option per item plus `All` and `None` (split into multiple questions if the 4-option limit is exceeded). Apply selected restorations.

On any restoration: restore the affected text via inverse `Edit` (re-insert `before`, remove `after`). For memory move-outs, also remove the appended snippet from the memory file and its corresponding entry from MEMORY.md (best effort).

Once complete, delete caches:

```bash
rm -f /tmp/restructure-claude-files-project-orig.md /tmp/restructure-claude-files-global-orig.md
```

End with a one-line summary: `Applied: N items. Advice: M items.`

## Step 6: Bridge to compact

If any `tighten` findings were recorded in Step 2, end with one line:

> The reviewers also surfaced N items that could be shortened in place. Run `/luca-kit:compact-claude-files` to apply them.

Substitute N with the actual count. Skip this step entirely if no tightenings were noted.
