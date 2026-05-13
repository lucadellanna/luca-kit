---
name: targeted-review
description: Single-file code review with a file-specific checklist. Phase 1 derives a checklist (or accepts a user-supplied one); Phase 2 spawns a subagent that emits bug-only findings against that checklist using a structural FINDINGS marker. Trigger phrases: "/targeted-review", "targeted review", "focused review of <file>", "deep review this file", "review <file> for logic bugs", "review this file with a custom checklist".
version: 0.1.0
---

# Targeted Review

Two-phase, single-file code review that catches file-specific bugs the standard reviews miss. The main agent derives (or accepts) a checklist tailored to this file's invariants and failure modes. A subagent then executes the checklist with bug-only output, parsed via a structural marker.

## When to use

- First-pass review of a single file before committing, especially when the file has non-obvious invariants the standard lenses would not know to check.
- Ad-hoc review of one file you suspect has logic bugs the broad reviews would miss.
- After implementing a non-trivial function.
- When `triple-review` returns clean but you want a tighter pass on a specific file.

## When NOT to use

| Situation | Use instead |
|---|---|
| Multi-file or whole-PR review | `triple-review`, `open-pr` |
| Style/convention enforcement | `specs-adherence-review` |
| Diff review or CI-driven fixes | `gemini-review`, `review-loop` |
| File over ~1000 lines | Scope to a function or section, then run this skill |

## Inputs

| Input | Required | Notes |
|---|---|---|
| Target file path | yes | Resolved to absolute in Step 0. One file per invocation |
| Checklist | no | Inline text or path to a `.md`. If omitted, main agent derives one |

## Steps

0. **Resolve and validate the target path.** Run via Bash:

   ```
   python3 -c "import os, sys; p = os.path.realpath(sys.argv[1]); assert os.path.isfile(p), f'not a file: {p}'; print(p)" "<input-path>"
   ```

   Use the resolved absolute path everywhere below. If the command exits non-zero, tell the user plainly: "Couldn't find a file at `<input-path>`. Check the path and try again." Do not surface the raw Python `AssertionError`.

1. **Determine checklist source.**
   - User supplied a checklist inline: use it; jump to Step 3.
   - User supplied a checklist path: use Read to load it. If the file is empty or Read failed, stop and report. Jump to Step 3.
   - Otherwise: continue to Step 2.

2. **Derive the checklist (main agent).** Read the target file in full. Write 5 to 15 checklist items.
   - The main agent does this, not a subagent. The main agent reads the file once; the subagent receives only the path and the checklist, never the file content. See DESIGN.md.
   - Each item names a *specific failure mode* in this specific file. Format: `<area>: <failure mode>, e.g., <concrete example tied to a line, function, or invariant>`.
   - Prioritize execution-path items: for each data transformation, shell invocation, conditional branch, and user-facing label in the file, ask "what breaks at the boundary?" Specifically look for: delimiter or metacharacter assumptions in parsing steps; missing flags in shell/grep invocations; ambiguous option labels in multi-choice prompts; redundant tool calls where context already holds the needed value; and empty/falsy/zero-count edge cases in each conditional branch.

3. **Spawn the execution subagent.** Use the Agent tool with:
   - `subagent_type`: `general-purpose`
   - `model`: `sonnet`
   - `description`: `Targeted checklist review`
   - `prompt`: the template below, with `<absolute-path>` and `<numbered list>` filled in.

   Prompt template (verbatim):

   ```
   Review the file at <absolute-path> against the checklist below. Do not derive your own checklist; only execute the items listed. You must read the file fully before producing findings.

   CHECKLIST:
   <numbered list>

   OUTPUT FORMAT (strict structural contract):
   Your response must begin with the exact line:
   FINDINGS:

   After that line, emit one block per checklist item where you found a bug, in this exact format:

   [Area name] - BUG
   Line N: <quoted code>
   Failure mode: <one sentence>
   Fix: <corrected code>

   For checklist items with no bug: emit no block. No "OK" lines, no preamble, no summary, no narration before or after.

   If you cannot read the file, your entire response must be the literal string: ERROR: cannot read file
   If you find no bugs in any item, emit only the FINDINGS: line and nothing else after it.
   ```

4. **Parse and present findings.**
   - If the output contains the line `ERROR: cannot read file`: stop and surface the error.
   - If the output contains a `FINDINGS:` line: take everything after that line; identify finding blocks by locating lines that match the pattern `[Area name] - BUG` (starts with `[`, contains `] - BUG`). Each such line opens a new block; count these as the parsed finding count.
   - If the output does NOT contain `FINDINGS:` (malformed): re-spawn ONCE with the same filled prompt verbatim (i.e., the prompt as actually sent in the first attempt, with `<absolute-path>` and `<numbered list>` already substituted). If the second attempt is also malformed, show the raw output to the user and stop.
   - If the parsed finding count is 0: report "no bugs found" and stop.
   - If the parsed finding count is >=1: report all findings to the user (area name + failure mode for each), then proceed to Step 5 to apply all of them.

5. **Apply all findings.** Apply findings in line-number order (earliest first); parse the line number from each finding's "Line N:" field (take the first integer after "Line "); if the subagent emits a range (e.g., "Line 42-45:"), use the lower bound; if no line number is present, place that finding last. For each finding:
   - **Uniqueness pre-flight.** Before each Edit, Grep the file for the quoted code from the finding's "Line N: `<quoted code>`" field (this is `old_string`) using literal (fixed-string) matching -- pass `-F` if invoking grep directly, or use the Grep tool's literal mode to avoid metacharacter interpretation (since `old_string` may contain regex metacharacters such as `*`, `[`, `.`, `(`, `)`). If count > 1, extend `old_string` with 2 to 3 surrounding lines and re-check; repeat up to 3 expansions; if still non-unique, apply the fix to the occurrence whose line number is closest to the reported "Line N" value. If count is 0, the subagent paraphrased rather than quoted verbatim: re-read the file at the reported line number, locate the closest matching code, and use that as `old_string`.
   - **Adjacency check.** If a later finding targets lines already edited or directly adjacent, re-read the file at the reported line, re-derive the fix against the current file state, and apply it.
   - Apply each Edit one at a time. Re-read the file before subsequent Edits.

## Anti-patterns

- Generic checklist items ("check error handling", "look for edge cases"). Every item must name a specific failure mode in this specific file.
- Modifying the prompt template on a re-spawn. Re-spawn means re-issue the same template verbatim, not a "softer" variant.
- Deriving the checklist from a section or summary of the file rather than reading it in full. Cross-function interactions and module-level invariants only surface when the full file is read.
- Re-reading the target file only once before all Edits rather than before each Edit. A prior Edit shifts line numbers; subsequent Edits using stale context apply to the wrong location.

## Scope

This skill does NOT cover: multi-file review, diff review, style/convention enforcement, test execution, typecheck. One file per invocation.

## Self-reflection

During execution, follow the self-observation protocol (see `${CLAUDE_PLUGIN_ROOT}/CLAUDE.md`, Principles).

**Skip condition.** If no findings were applied in Step 5 (because none were parsed in Step 4), skip the rest of this section. The scorer requires applied `old_string -> new_string` pairs; without them, the Fix correctness criterion is unscoreable.

When at least one finding was applied, spawn a Haiku sub-agent. Pass it: (a) the contents of this SKILL.md (inline in the sub-agent prompt, not as a path reference, since `${CLAUDE_PLUGIN_ROOT}` may not resolve in the sub-agent's session), (b) the final checklist used, (c) the subagent's raw output, (d) the list of applied Edits as `old_string -> new_string` pairs. Score each criterion 0 to 10. If the average is below 9.5 or any criterion remains below 8, draft a concise SKILL.md edit to prevent recurrence, show it to the user, and apply on approval.

Criteria (MECE):
- **Checklist specificity**: every checklist item names a concrete failure mode tied to a line, function, or invariant. Generic items score 0.
- **Prompt completeness**: the subagent prompt template unambiguously specifies the `FINDINGS:` marker, the error path, and the no-bug case.
- **Contract compliance**: the subagent's raw output started with `FINDINGS:` (or the literal `ERROR: cannot read file`), with no preamble or summary before the marker.
- **Fix correctness**: each applied Edit's `new_string` is syntactically well-formed and directly addresses the failure mode stated in the finding (scorable from the old/new pair and the failure-mode description alone).
