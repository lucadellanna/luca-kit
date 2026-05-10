---
name: Triple Review
description: Three-lens parallel code review against principles, recurring bug patterns, and structural integrity. Invoked by open-pr before pushing; also usable standalone.
version: 0.1.0
---

# Triple Review

Runs three independent Sonnet sub-agents in parallel on the diff vs the base branch. Returns a consolidated finding list sorted by severity.

## Inputs

- **Base branch**: passed in by caller (e.g. `main`). If invoked standalone, detect with `git remote show origin | grep 'HEAD branch' | awk '{print $NF}'`.
- **Diff scope**: `git diff origin/<base>...HEAD` against the remote tracking ref: local `<base>` may be missing or stale in feature-branch clones.

## Step 1: Get changed files and diff

```bash
BASE=<base_branch>
git fetch origin "$BASE" --quiet 2>/dev/null || true   # ensure remote ref is current
git diff "origin/$BASE"...HEAD --name-only             # list of changed files
git diff "origin/$BASE"...HEAD                         # full diff for sub-agents
```

If diff is empty: report "Nothing to review vs $BASE" and stop.

## Step 2: Spawn three Sonnet sub-agents in parallel

Send all three Agent tool calls in a single message so they run concurrently.

---

**Lens A: Principles** (`subagent_type: general-purpose`, `model: sonnet`)

Prompt:
```
You are doing a code review focused on principle violations.

1. Read ~/.claude/CLAUDE.md and, if it exists, ./CLAUDE.md and/or ./AGENTS.md (local project rules).
2. Extract every actionable rule from these files. Skip section headers, narrative prose, and examples.
3. Read the following git diff:

<diff>
[full diff text]
</diff>

4. For each rule, check if the diff violates it. Skip rules clearly irrelevant to the diff's language or domain.
5. Report each violation as exactly:
   SEVERITY | FILE:LINE | RULE | PROBLEM | FIX
   where SEVERITY is one of: CRITICAL (rule says NEVER/MUST/non-negotiable, or data-loss/security risk) | IMPORTANT (clear guidance missed) | MINOR (style or optional improvement)
6. If no violations found, output exactly: CLEAN

Output ONLY the violation lines or CLEAN. No preamble.
```

---

**Lens B: Recurring patterns** (`subagent_type: general-purpose`, `model: sonnet`)

Prompt:
```
You are doing a code review focused on recurring bug patterns.

1. Read ~/.claude/code-review-checklist.md.
2. Read the following git diff:

<diff>
[full diff text]
</diff>

3. For each checklist item, check if the diff contains the anti-pattern.
4. Report each match as exactly:
   FILE:LINE | PATTERN | SPECIFIC PROBLEM
5. If no matches, output exactly: CLEAN

Output ONLY the match lines or CLEAN. No preamble.
```

---

**Lens C: Structural integrity** (`subagent_type: general-purpose`, `model: sonnet`)

Prompt:
```
You are doing a structural code review. Check the following diff for four specific issues:

(a) PROSE-CODE DRIFT: behavior described in prose or a comment that is not implemented in the adjacent code block.
(b) THRESHOLD MISMATCH: a numeric threshold or limit in code (awk filter, jq select, head -N, array index) that contradicts the value stated in surrounding prose or sibling steps.
(c) FALLBACK CHAIN: a conditional fallback (if/else, X or Y, X ?? Y) where an intermediate value can produce an empty string, None, or other falsy that bypasses the intended fallback. Flag os.path.basename("/"), str.split() on empty string, dict.get() with no default.
(d) SHELL PIPELINE: a sort | uniq -c pipeline where input lines contain a source/identifier field: the count reflects occurrence of that exact pair, not occurrence of the value across distinct identifiers.

<diff>
[full diff text]
</diff>

Report each issue as exactly:
CATEGORY | FILE:LINE | SPECIFIC PROBLEM | FIX
where CATEGORY is one of: PROSE-CODE-DRIFT | THRESHOLD-MISMATCH | FALLBACK-CHAIN | SHELL-PIPELINE

If no issues found, output exactly: CLEAN

Output ONLY the issue lines or CLEAN. No preamble.
```

---

## Step 3: Consolidate findings

Wait for all three sub-agents. Then:

1. Collect all non-CLEAN lines.
2. Deduplicate: if two lenses flag the same file+line for the same issue, keep the more specific description.
3. Assign a severity to Lens B and C findings:
   - Any finding touching a NEVER/MUST rule = CRITICAL
   - All others from Lens B/C = IMPORTANT
4. Sort: CRITICAL first, then IMPORTANT, then MINOR.

## Step 4: Return findings

Report as a table:

| Severity | File:Line | Category | Problem | Fix |
|---|---|---|---|---|
| CRITICAL | ... | ... | ... | ... |
| ... | | | | |

Then summarise counts: `N critical, N important, N minor`.

If all three lenses returned CLEAN: report `CLEAN: no issues found across all three lenses.`
