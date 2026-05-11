---
name: PreToolUse hook blocks compound git commands
description: PreToolUse hooks fire before the entire Bash command runs; git add && git commit compound commands fail to stage when the hook blocks on the commit portion
type: feedback
---

Always run `git add` in a separate Bash call before `git commit` when a PreToolUse hook is active.

**Why:** The PreToolUse hook fires before any part of the Bash tool executes. A compound `git add X && git commit ...` command triggers the hook on the full string; if the hook blocks, `git add` never runs. The fix is two separate Bash calls: one to stage (which doesn't match the `git commit*` hook condition), then verify staging is clean, then commit.

**How to apply:** When a commit is blocked by a PreToolUse hook, always check whether the staging step in the same compound command actually ran before diagnosing the root cause.
