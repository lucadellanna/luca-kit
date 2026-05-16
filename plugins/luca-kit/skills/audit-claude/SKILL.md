---
name: audit-claude
description: >
  Tightens your project's ./CLAUDE.md and your global ~/.claude/CLAUDE.md
  by removing redundancy and content that belongs elsewhere. Flags items
  that may be in the wrong scope. Applies cleanups automatically; asks
  for input only if a safety check spots something important.
version: 0.3.0
---

# Audit Claude

Audits both the project `./CLAUDE.md` and the global `~/.claude/CLAUDE.md`. Removes cruft within each file and flags scope mismatches between them.

Trust model:

- **Reviewers** (read-only) propose changes.
- **Orchestrator** applies them automatically.
- **Verifier** catches accidental loss of important info.
- **User** intervenes only if the verifier flags something.

## Step 1: Resolve files

```bash
PROJECT="$(pwd)/CLAUDE.md"
GLOBAL="$HOME/.claude/CLAUDE.md"
echo "project: $(test -f "$PROJECT" && wc -l < "$PROJECT" || echo missing)"
echo "global: $(test -f "$GLOBAL" && wc -l < "$GLOBAL" || echo missing)"
```

If both are missing, say "No CLAUDE.md found (project or global)." and stop. Label the files that exist as **targets**.

## Step 2: Run reviewers in parallel

Send all Agent calls in a single message. Each reviewer reads the file itself; the orchestrator does not load file contents into main context.

**Per target** (each file that exists):

- `subagent_type: "luca-kit:claude-md-structural-reviewer"`: prompt is the target's absolute path.
- `subagent_type: "luca-kit:claude-md-compression-reviewer"`: prompt is the target's absolute path.

**If both targets exist**, also run:

- `subagent_type: "luca-kit:claude-md-scope-reviewer"`: prompt is two lines, the project file path then the global file path.

The scope reviewer returns promote (project to global), demote (global to project), and duplicate findings.

Each agent's mandate, finding categories, and output format are defined in the agent's own file. Do not duplicate them here.

If all reviewers return zero findings, say "Nothing to surface." and stop.

## Step 3: Cache and apply

Cache each target:

```bash
test -f "$PROJECT" && cp "$PROJECT" /tmp/audit-claude-project-orig.md
test -f "$GLOBAL"  && cp "$GLOBAL"  /tmp/audit-claude-global-orig.md
```

Apply structural and compression findings per file without asking the user. Routing:

| Finding | Action |
|---|---|
| Tightening | `Edit`: replace `before` with `after` (empty string if `after` is `(remove)`) |
| Compression | `Edit`: replace `before` with `after` |
| Move-out to co-located memory dir | (1) Check if snippet already exists in target; skip if duplicate. (2) Append with a leading newline (create if absent). (3) If the memory directory has an index file (MEMORY.md), add a one-line entry pointing to the new file. (4) Edit: remove from the CLAUDE.md. |
| Move-out, any other target | Do not apply. Carry forward to Step 5 as advice. |

**Co-located memory directories:** for `./CLAUDE.md` that is `./.claude/memory/`; for `~/.claude/CLAUDE.md` that is `~/.claude/memory/`.

**Scope-transfer findings** (promote, demote, duplicate) are never auto-applied. Carry all to Step 5 as advice.

If any `Edit` fails because the `before` snippet is gone (a prior edit overlapped it), note as skipped and continue.

## Step 4: Verify

Send one Agent call per target that was modified:

- `subagent_type: "luca-kit:claude-md-loss-verifier"`

Prompt: two lines, the cached original then the current file. For the project file: `/tmp/audit-claude-project-orig.md` and the project path. For the global file: `/tmp/audit-claude-global-orig.md` and the global path.

The verifier returns either `No meaningful content lost.` or a bulleted list of important losses.

## Step 5: Report and react

Show per target (skip a target section if it had no findings):

1. **Applied** (project / global): one line per change applied. Include skipped/duplicate notes.
2. **Advice**: non-memory move-outs (snippet + suggested destination). Empty section omitted.
3. **Scope transfers**: promote, demote, and duplicate recommendations with rationale. Empty section omitted.
4. **Verifier result**: verbatim, per target.

If all verifiers returned `No meaningful content lost.`: delete caches and stop.

If any verifier flagged something, call `AskUserQuestion`:

> "The verifier flagged the above as possibly important. Restore?"

Two options: `Restore all` (restores all cached originals, undoes memory appends), `Keep changes`. On `Restore all`, also remove any snippets appended to memory files in Step 3 (best effort).

(Selective per-item restoration is out of scope for this version. All-or-nothing keeps the safety net deterministic.)

Once complete, delete caches:

```bash
rm -f /tmp/audit-claude-project-orig.md /tmp/audit-claude-global-orig.md
```
