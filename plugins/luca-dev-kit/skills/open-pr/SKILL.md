---
name: Open PR
description: Pre-PR quality gates + PR creation + autonomous review-loop handoff. Trigger: "open pr", "create pr", "/open-pr", or "ship". After invocation, no further user input is needed until review-loop exits or hits a stop condition.
version: 0.1.0
---

# Open PR

Orchestrates the full pre-PR pipeline, creates the PR, and hands off to the autonomous review loop.

## Step 1: Commit state check

```bash
git status --short
```

If uncommitted changes exist: offer to commit them via `commit-commands:commit`. If user declines, warn "Uncommitted changes will not be in the PR" and continue.

## Step 2: Detect base branch and diff

```bash
BASE=$(git remote show origin | grep 'HEAD branch' | awk '{print $NF}')
[[ -z "$BASE" ]] && { echo "Error: Could not detect base branch from origin." >&2; exit 1; }
git fetch origin "$BASE" --quiet 2>/dev/null || true   # ensure remote ref is current
DIFF=$(git diff "origin/$BASE"...HEAD)
```

Use `origin/$BASE` (the remote tracking ref) rather than the local branch name: local `main` may be missing or stale in feature-branch clones.

If diff is empty: "Nothing new vs $BASE: commit your changes first." Stop.

## Step 3: Detect PR shape

Check if ALL changed files are purely structural (no logic added or modified):
```bash
git diff "origin/$BASE"...HEAD
```

Use git's own tools -- token scanning misses content changes in languages not covered by the list (constants, config strings, CSS, SQL, etc.).

```bash
# Pure renames/moves only (R100 = 100% similarity, no content change)
NON_RENAMES=$(git diff "origin/$BASE"...HEAD --name-status | grep -v '^R100' | wc -l | tr -d ' ')

# Whitespace/blank-line only changes (empty diff = formatting only)
CONTENT_DIFF=$(git diff "origin/$BASE"...HEAD -w --ignore-blank-lines)
```

Structural-only if `NON_RENAMES == 0` (all changes are pure renames) OR `CONTENT_DIFF` is empty (only whitespace changed). Any other combination: run review.

If structural-only: skip steps 4–5 (no review needed). Jump to step 6.

## Step 4: Triple review (pass 1)

Invoke `luca-dev-kit:triple-review`. Pass the base branch name.

Wait for completion. Receive consolidated finding table with counts.

## Step 5: Triage and fix

**If CLEAN:** proceed to step 6.

**If findings exist:**
- Fix all CRITICAL and IMPORTANT findings now. For large fix sets, spawn a Sonnet sub-agent per file group.
- Note MINOR findings: include them in the PR body as "Known minor items".
- After fixes: commit with `git commit -m "fix: pre-PR self-review"`.

**Re-run condition:** if pass 1 had ≥1 CRITICAL or ≥3 IMPORTANT findings, run `luca-dev-kit:triple-review` once more (pass 2). Apply any new CRITICAL/IMPORTANT fixes and commit. Hard cap: no pass 3.

## Step 6: Pre-commit hook check (first run only)

```bash
grep -q "luca-dev-kit" "$(git rev-parse --show-toplevel)/.git/hooks/pre-commit" 2>/dev/null || echo "not-installed"
```

If not installed: invoke `luca-dev-kit:install-pre-commit-hooks`.

## Step 7: Typecheck (always runs, ignores timing cache)

Detect and run type checker:

1. Check `package.json` for scripts `typecheck`, `type-check`, or `tsc`.
   - Detect package manager: `pnpm-lock.yaml` → pnpm, `yarn.lock` → yarn, else npm.
   - Run: `<pm> run <script>`
2. Else if `tsconfig.json` exists: `npx --no-install tsc --noEmit`
3. Else if mypy configured (`mypy.ini` or `[tool.mypy]` in `pyproject.toml`): `mypy .`
4. Else if `Cargo.toml`: `cargo check`
5. Else if `go.mod`: `go vet ./...`
6. Else: skip with note "No type checker detected."

**On error: stop.** Do not push with type errors. Report the errors and ask user to fix.

## Step 8: Push

```bash
BRANCH=$(git branch --show-current)
IS_REMOTE=$(git branch -r | grep "origin/$BRANCH" || true)

if [[ -z "$IS_REMOTE" ]]; then
  git push -u origin "$BRANCH"
else
  git push
fi
```

## Step 9: Create PR

```bash
gh pr create --base "$BASE" \
  --title "<conventional-commit-style title from branch name + commits>" \
  --body "$(cat <<'EOF'
## Summary
<1–3 bullets from commit messages: what changed and why>

## Test plan
<bulleted checklist of what to verify manually>

## Minor items (not blocking)
<list from step 5, or omit if empty>
EOF
)"
```

Capture PR number from output: `gh pr view --json number -q '.number'`

## Step 10: Write state file and hand off

Write `.claude/cache/review-loop-state.json` atomically (tmp + os.replace to prevent partial writes):

```bash
PR_CREATED_AT=$(gh pr view --json createdAt -q '.createdAt')
PR_NUM=$(gh pr view --json number -q '.number')

# All values passed via env vars: never interpolated into Python source.
PR_NUM="$PR_NUM" BASE="$BASE" PR_CREATED_AT="$PR_CREATED_AT" python3 -c "
import json, os

state = {
    'pr_number': int(os.environ['PR_NUM']),
    'base_branch': os.environ['BASE'],
    'round': 0,
    'trigger_ts': os.environ['PR_CREATED_AT'],
    'thread_hashes_prev': None
}

os.makedirs('.claude/cache', exist_ok=True)
tmp = '.claude/cache/review-loop-state.json.tmp'
with open(tmp, 'w') as f:
    json.dump(state, f, indent=2)
os.replace(tmp, '.claude/cache/review-loop-state.json')
"
```

Ensure `.claude/cache/` is in `.gitignore`: check with `grep -qE '^\.claude/cache/' .gitignore` and append with newline guard if missing:
```bash
if ! grep -qE '^\.claude/cache/' .gitignore 2>/dev/null; then
  python3 -c "
import os
p = '.gitignore'
if os.path.exists(p):
    with open(p, 'rb+') as f:
        f.seek(0, 2)
        if f.tell() > 0:
            f.seek(-1, 2)
            if f.read(1) != b'\n':
                f.write(b'\n')
"
  printf '.claude/cache/\n' >> .gitignore
fi
```

Then immediately invoke `luca-dev-kit:review-loop`. Pass the PR number. The loop runs autonomously from here: no further user input expected until a stop condition fires.

## Design decisions

| Decision | Rationale |
|---|---|
| `git remote show origin` for base branch detection (not `git symbolic-ref`) | `git symbolic-ref refs/remotes/origin/HEAD` is not reliably set in all clone types (shallow, sparse). `git remote show origin` is consistent across all three skills and the subsequent `git fetch` already incurs network I/O. |
| Remote name hardcoded to `origin` (not dynamic detection) | Dynamic detection via `git remote | head -n 1` is unreliable: remotes have no defined ordering. `origin` is the standard convention and is used consistently for push and PR creation throughout all three skills. Fork-based workflows where the primary push remote differs from `origin` are out of scope. |
| Structural detection uses git tools, not token scanning | Token scanning misses content changes that don't use listed keywords (constants, config strings, CSS, SQL). `git diff --name-status | grep -v '^R100'` and `git diff -w --ignore-blank-lines` are language-agnostic and reliable. |
