# Design decisions

| Decision | Rationale |
|----------|-----------|
| OWNER/REPO fetched per-round (not cached in state file) | Each round is a separate Claude invocation via ScheduleWakeup. OWNER/REPO are fetched once per round in step C -- not in a tight inner loop. Caching in the state file adds state management complexity for negligible gain (one extra API call per round among many). |
