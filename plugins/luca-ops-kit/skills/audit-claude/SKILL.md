---
name: audit-claude
description: Audit local and global CLAUDE.md and MEMORY.md files for conciseness and cross-file redundancy. Lists files by line count, lets user choose which to consider, proposes optimizations, implements on approval, then verifies no meaningful content was lost.
version: 0.4.3
---

# Audit Claude

Audit CLAUDE.md and MEMORY.md files for bloat and redundancy. Surface optimization opportunities across all selected files, implement on approval, verify nothing meaningful was lost.

## Step 1: Discover files

Check whether each path exists. Skip those that don't.

| Label | Path |
|-------|------|
| Global CLAUDE.md | `~/.claude/CLAUDE.md` |
| Global memory index | `~/.claude/MEMORY.md` |
| Global memory files | All `~/.claude/memory/*.md` |
| Project CLAUDE.md | `./CLAUDE.md` |
| Project memory index | `./MEMORY.md`, `./.claude/MEMORY.md`, `./.claude/memory/MEMORY.md` |

For each MEMORY.md found: extract all Markdown links (inline and reference-style), ignore external URLs (starting with http/https), strip any #fragment suffixes, and resolve to absolute paths (expand ~; relative paths resolve from the MEMORY.md directory). Add each resolved path to the audit list if it ends in .md, falls within ~/.claude/ or the CWD, and exists; otherwise note it as "out of scope: skipped" or "linked but missing: skipped". De-duplicate the final list (combining table-pattern files and link-extracted files).

If no files are found, say "No CLAUDE.md or MEMORY.md files found." and stop.

## Step 2: List files by length

Count the lines in each file. Present a table sorted by line count descending (longest first):

| File | Lines |
|------|-------|
| `~/.claude/CLAUDE.md` | 142 |
| `./CLAUDE.md` | 58 |
| … | … |

Note any missing linked files below the table.

## Step 3: Ask which to consider

Use `AskUserQuestion` (multiSelect, all files pre-selected, listed in the same descending-length order) with the message:

> "Which files would you like to audit?"

`AskUserQuestion` accepts at most 4 options per call. If there are more than 4 files, split into multiple consecutive calls (e.g., "1 of 2", "2 of 2") and aggregate all selected items before proceeding.

If the user selects none, stop.

## Step 4: Analyze selected files

Spawn two sub-agents **in parallel**; both read the selected files themselves using the paths provided:

**Sub-agent A: Sonnet (structural analysis):**

> You are auditing a set of configuration and memory files for a Claude Code environment. First, read every file at the paths listed below. Then analyze them together and identify:
>
> **Within-file opportunities** (per file):
> - Redundant phrasing or repeated points
> - Sections that could be expressed more concisely without losing meaning
>
> **Cross-file opportunities** (across files):
> - Content duplicated across files (same rule stated in multiple places)
> - Content in one file that belongs in another
> - Opportunities to consolidate or refactor
>
> For each opportunity, provide: which file(s) are affected, a short description, and the proposed change. For all changes (within-file or cross-file), provide a unique before snippet and the corresponding after snippet (or indicate the snippet should be removed). For additions, provide the exact text and surrounding context for placement. Do not rewrite files wholesale. Surface discrete, targeted changes only.
>
> Files to read (absolute paths, one per line):
> [list of selected absolute paths]

**Sub-agent B: Haiku (micro-compression pass):**

> Read each file at the paths listed below. For each file, identify sentence-level compression opportunities only:
> - Two sentences that can be merged into one without losing meaning
> - A verbose phrase that shortens to an equivalent form
> - A clause that restates what the surrounding sentence already implies
>
> For each opportunity: file path, exact before text, exact after text. The "after" must be semantically identical to "before": shorter, not different. Do not flag structural issues, cross-file redundancy, or anything requiring judgment about whether content is load-bearing.
>
> Files to read (absolute paths, one per line):
> [list of selected absolute paths]

Wait for both sub-agents to complete. Merge their findings: if a structural change from Sub-agent A moves or rewrites a sentence that Sub-agent B targets for micro-compression, prioritize the structural change and discard the conflicting micro-compression. If both can apply independently, keep both.

## Step 5: Present and confirm

Show findings in two groups: **Structural** (Sub-agent A) and **Micro-compressions** (Sub-agent B), each grouped by within-file and cross-file where applicable. Then present a compact summary table of all proposed changes (file | type | one-line description) so the user has a single reference when approving. Ask:

> "Shall I implement all of these changes?"

If the user declines, stop.

## Step 6: Implement changes

Before writing any file:
1. Verify its path is within `~/.claude/` or the current working directory; skip and report any file outside this scope.
2. Cache its current content to `/tmp/audit-claude-orig-<hash>.md` where `<hash>` is a unique hex digest of the full absolute path string (e.g., using `md5`, `md5sum`, or a similar hashing utility; take only the hex portion). MD5 of distinct paths never collides, avoiding the basename collision between e.g. `~/.claude/CLAUDE.md` and `./CLAUDE.md`.

Apply all proposed changes. Track which files were modified and the corresponding `/tmp/` cache path for each.

## Step 7: Verify no meaningful content was lost

Spawn a **Haiku sub-agent** with the list of modified file pairs (original cache path + live path) and this prompt:

> For each file pair below, read both the original (cached at the /tmp/ path) and the revised version (at the live path). Report any meaningful content that was removed or altered in a way that changes its intent: rules, constraints, examples, or context that a reader would miss. Ignore purely stylistic changes (rephrasing that preserves meaning, whitespace, formatting).
>
> For each file, return either "No meaningful content lost" or a bulleted list of specific losses.
>
> File pairs (original_cache_path → live_path):
> [list of /tmp/audit-claude-orig-<md5_of_path>.md → <live path> pairs]

Show the Haiku's report to the user. If any losses are flagged, ask for confirmation before restoring each affected file from its cached original in `/tmp/`. Once the audit and any restoration are complete, delete the specific cache files tracked in Step 6.

## Self-reflection

Spawn a Haiku sub-agent to score this run on these criteria (0–10 each), with the instruction: "Score net of documented decisions in the ## Design decisions section; do not penalise intentional trade-offs.":

1. **Discovery completeness**: all expected file types were found or correctly noted as absent; missing linked files were reported
2. **Analysis quality**: optimizations are specific and actionable; cross-file opportunities are identified where they exist
3. **Safety**: no file was written without user confirmation; scope check was applied
4. **Verification**: the post-write Haiku check correctly identified (or confirmed absence of) meaningful content loss

Compute the average.
- Average ≥ 9.5 → stop.
- Score increased by < 0.5 and all applied changes were objectively positive (additions or tightening only, no substantive content removed) → treat as Haiku variance; stop.
- Average < 9.5 and higher than the previous iteration → revise the skill output and re-score.
- Score declined or no improvement for any other reason → stop.

Maximum 3 total iterations. If any criterion remains below 8 after iteration, draft a concise edit to this SKILL.md to prevent the same failure, show it to the user, and apply on approval.

## Design decisions

| Decision | Rationale |
|----------|-----------|
| Line count instead of conciseness score | Line count is objective and instantly comparable; a score requires a sub-agent call per file before the user has even chosen what to audit |
| Single subagent sees all files together | Cross-file redundancy requires joint analysis; sequential per-file scoring misses it |
| Sonnet for analysis (not Haiku) | Identifying load-bearing content vs. bloat requires judgment; Haiku risks flagging necessary context as redundant |
| Haiku for post-write verification | Safety check is pattern-matching (find what was removed), not judgment; Haiku is sufficient and cheaper |
| Single approval for all changes | Reduces friction; the post-write Haiku provides a safety net that makes per-change approval unnecessary |
| Scope check applied at discovery (Step 1) and enforced again at write (Step 6) | Out-of-scope files are excluded before being read or sent to a sub-agent; the write guard is belt-and-suspenders, not the primary control |
| Conductor workspace memories excluded from scope | `~/.claude/projects/*/memory/MEMORY.md` spans all past workspaces including closed ones; ephemeral and not load-bearing |
| Files read by sub-agents, not main context (Steps 4 and 7) | Avoids loading file contents into the main context window; all source material stays in sub-agent contexts, reducing context pollution across long audit runs |
| Originals cached to `/tmp/` with MD5-hashed filenames before Step 6 writes | Enables Haiku verification without holding original content in the main context; MD5 of the full path is collision-free across files that share a basename (e.g. `~/.claude/CLAUDE.md` vs `./CLAUDE.md`) |
| POSIX tools assumed (`/tmp/`, md5/md5sum) | Claude Code runs on macOS and Linux; Windows is out of scope for this skill |
| Parallel Haiku micro-compression pass (Step 4B) | Sonnet gravitates toward structural/cross-file findings and misses sentence-level compression; a dedicated Haiku pass with a narrow prompt catches what Sonnet leaves behind, at no extra latency since both run in parallel |
