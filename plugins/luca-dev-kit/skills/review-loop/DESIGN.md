# Design decisions

| Decision | Rationale |
|----------|-----------|
| OWNER/REPO fetched per-round (not cached in state file) | Each round is a separate Claude invocation via ScheduleWakeup. OWNER/REPO are fetched once per round in step C -- not in a tight inner loop. Caching in the state file adds state management complexity for negligible gain (one extra API call per round among many). |
| OWNER/REPO extracted from PR URL (not `--json repository`) | `gh pr view --json repository` is not a valid field in the gh CLI. Parsing `owner/repo` from `--json url` (always `https://github.com/{owner}/{repo}/pull/{N}`) is reliable and works in all GitHub environments including Enterprise. |
| FIX_THREADS_JSON passed via env var (not stdin/printf) | Both `printf '%s' "$VAR" | python3` and `VAR="$VALUE" python3` pass the value as a command argument subject to the same ARG_MAX limits. Env var is cleaner. Typical PR thread data is well under 50KB; the limit is not a practical concern. |
| No lockfile on `~/.claude/code-review-checklist.md` | Claude processes one task per session; true concurrent writes require multiple simultaneous Claude sessions, which is uncommon. The checklist is human-curated; a corrupted line is trivially noticed and fixed. Lockfile overhead is not justified. |
