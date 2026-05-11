---
name: specs-adherence-review
description: Review changed code for adherence to principles in ~/.claude/CLAUDE.md and local CLAUDE.md/AGENTS.md. Use before PRs, when user says "check specs", "adheres to principles?", or "specs review". Also invoked as Lens A by luca-dev-kit:triple-review.
version: 0.1.0
---

# Specs Adherence Review

Systematically check changed code against every rule in the active specs files.

## Scope

| Source | Path | Priority |
|---|---|---|
| Global principles | `~/.claude/CLAUDE.md` | Baseline |
| Local principles | `./CLAUDE.md` and/or `./AGENTS.md` | Overrides global |

Local rules win over global where they conflict. Ignore rules clearly irrelevant to the diff's language or domain.

## Procedure

### 1. Get the diff

```bash
# Prefer staged; fall back to all uncommitted; fall back to diff vs remote base branch
git diff --cached --stat
git diff --stat
BASE=$(git remote show origin | grep 'HEAD branch' | awk '{print $NF}')
git fetch origin "$BASE" --quiet 2>/dev/null || true
git diff "origin/$BASE"...HEAD
```

Use `origin/$BASE` (remote tracking ref) rather than the local branch name: local `main` may be missing or stale in feature-branch clones.

Use the first non-empty result as the review scope.

### 2. Load specs

Read both files fully. Extract every **actionable rule**: skip section headers, narrative prose, and examples. Group by file.

### 3. Check each rule

For every rule, scan the diff for a violation. Skip rules clearly irrelevant to the diff's language or domain.

| Severity | Meaning |
|---|---|
| **Critical** | Rule says NEVER/MUST/non-negotiable, or data-loss/security/correctness risk |
| **Important** | Clear guidance that was missed |
| **Minor** | Style, wording, or optional improvement |

### 4. Report

For each violation:

```
## [Severity] Rule violated: [rule summary]
**Source:** `~/.claude/CLAUDE.md` OR `./CLAUDE.md:section`
**Location:** `path/to/file:line`
**Problem:** [what the code does vs what the rule requires]
**Fix:** [concrete change needed]
```

If no violations: say so explicitly and list which rules were checked.

### 5. Prioritise fixes

- Critical: block commit, fix first
- Important: fix or get explicit acknowledgement before committing
- Minor: note, leave to user's discretion

Do NOT auto-fix without asking. Offer to apply fixes after showing the report.

## Notes

- Checks principles only. For DRY/design tokens/hoisting, use a separate code-standards review.
- If diff is empty and no base branch exists, say so and stop.
- Em dashes (U+2014) are caught by the luca-dev-kit pre-commit hook. This skill does not need to scan for them.
- **Pre-PR scan**: invoked by `luca-dev-kit:open-pr` against the full branch diff. When run standalone pre-commit, it catches issues accumulated across earlier commits that per-commit scans miss.
