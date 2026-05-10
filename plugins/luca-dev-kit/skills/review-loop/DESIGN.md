# Design decisions

| Decision | Rationale |
|----------|-----------|
| OWNER/REPO fetched per-round (not cached in state file) | Each round is a separate Claude invocation via ScheduleWakeup. OWNER/REPO are fetched once per round in step C -- not in a tight inner loop. Caching in the state file adds state management complexity for negligible gain (one extra API call per round among many). |
| OWNER/REPO extracted from PR URL (not `--json repository`) | `gh pr view --json repository` is not a valid field in the gh CLI. Parsing `owner/repo` from `--json url` (always `https://github.com/{owner}/{repo}/pull/{N}`) is reliable and works in all GitHub environments including Enterprise. |
