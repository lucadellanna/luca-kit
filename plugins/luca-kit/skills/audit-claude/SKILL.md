---
name: audit-claude
description: >
  Tightens your project's ./CLAUDE.md by removing redundancy and content
  that belongs elsewhere. Applies cleanups automatically; asks for input
  only if a safety check spots something important that may have been
  removed by mistake.
version: 0.2.0
---

# Audit Claude

The skill removes cruft from `./CLAUDE.md` without interrogating the user about every finding. Trust model:

- **Reviewers** (read-only) propose changes.
- **Orchestrator** applies them automatically.
- **Verifier** catches accidental loss of important info.
- **User** intervenes only if the verifier flags something.

## Step 1: Confirm the file exists

```bash
test -f ./CLAUDE.md && wc -l ./CLAUDE.md || echo "missing"
```

If `missing`, say "No `./CLAUDE.md` found in this directory." and stop. Otherwise show the line count.

## Step 2: Run two reviewers in parallel

Send a single message with two `Agent` calls. Both reviewers read the file themselves; the orchestrator does not load it into main context.

- `subagent_type: "luca-kit:claude-md-structural-reviewer"`: returns tightenings and move-outs.
- `subagent_type: "luca-kit:claude-md-compression-reviewer"`: returns micro-compressions.

Each prompt: one line, the absolute path to `./CLAUDE.md` (resolve via `pwd`).

Each agent's mandate, finding categories, and output format are defined in the agent's own file. Do not duplicate them here.

If both reviewers return zero findings, say "Nothing to surface." and stop.

## Step 3: Cache and apply

Cache the file:

```bash
cp ./CLAUDE.md /tmp/audit-claude-orig.md
```

Apply each finding without asking the user. Routing:

| Finding | Action |
|---|---|
| Tightening | `Edit`: replace `before` with `after` (empty string if `after` is `(remove)`) |
| Compression | `Edit`: replace `before` with `after` |
| Move-out, target path under ./.claude/memory/ | (1) Check if the exact snippet exists in the target file as a block; if found, skip and note as duplicate. (2) Append the snippet to the target file with a leading newline (create the file if absent). (3) Edit: remove the snippet from CLAUDE.md. |
| Move-out, any other target (global memory, path-rule, skill, hook, template) | Do not apply. Carry forward to Step 5 as advice. |

Order of `Edit` calls within CLAUDE.md does not matter (Edit uses string matching, not byte offsets), but if any `Edit` fails because the `before` snippet is no longer present (a prior edit overlapped it), note it as skipped and continue with the rest.

## Step 4: Verify

Send one `Agent` call:

- `subagent_type: "luca-kit:claude-md-loss-verifier"`

Prompt: two lines, the absolute path to `/tmp/audit-claude-orig.md` (original) and the absolute path to `./CLAUDE.md` (revised).

The verifier returns either `No meaningful content lost.` or a bulleted list of important losses, calibrated to the "load-bearing rule application" bar in its own agent file.

## Step 5: Report and react

Show:

1. **Applied**: one line per change actually applied (tightening, compression, project-memory move-out). Include skipped/duplicate notes.
2. **Advice**: non-memory move-outs (snippet + suggested destination). Empty section omitted.
3. **Verifier result**: verbatim.

If the verifier returned `No meaningful content lost.`: delete the cache and stop.

If the verifier flagged anything, call `AskUserQuestion`:

> "The verifier flagged the above as possibly important. Restore?"

Two options: `Restore all` (runs `cp /tmp/audit-claude-orig.md ./CLAUDE.md`, undoing every applied change), `Keep changes`. On `Restore all`, also remove any snippets that were appended to memory files in Step 3 (best effort: `grep -B1 -A1 -F` for the snippet, remove the matching block).

(Selective per-item restoration is out of scope for this version: tightenings and compressions are reversible by swapping `before` and `after`, but memory move-outs require coordinated multi-file undo. All-or-nothing keeps the safety net deterministic.)

Once complete, delete the cache:

```bash
rm -f /tmp/audit-claude-orig.md
```
