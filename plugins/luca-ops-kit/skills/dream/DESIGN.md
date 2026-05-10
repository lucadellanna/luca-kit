# Design decisions

| Decision | Rationale |
|----------|-----------|
| /dream never writes to .jsonl logs | Logs are append-only; only /reflect writes. Prevents dream contaminating its own input corpus. |
| Scope defaults to current repo | Least-surprise default; `all` requires explicit opt-in. |
| `all` mode pre-aggregates via jq | Raw multi-repo logs overflow model context; jq extracts only threshold-meeting candidates before the model sees them. |
| Pre-load threshold ≥2 (below Step 2's ≥3 bar) | Conservative buffer: loads borderline candidates so Step 2 analysis can apply the stricter filter without risk of missing anything. Step 2 performs the authoritative ≥3 check. |
| Glob guard before jq pipelines | Unmatched glob in nullglob shells passes no args to `jq -rn`, causing it to block on stdin; in non-nullglob shells it passes the literal glob string as a filename. The guard exits early cleanly. |
| 90-day default window | Balances recency with capturing never-acted-on patterns that may be older. |
| `--dry-run` flag | Builds user trust before any writes; recommended for first run. |
| `memory_target` for contradiction detection | Structured field lookup is reliable; free-text NLP comparison is not. Schema 1 only; schema 2 logs lack this field. |
| Dual-schema support (1 and 2) | Schema 1: structured findings with type/text/skill/memory_target/actions_taken (legacy /reflect). Schema 2: plain string findings (current /reflect). Text-matching signals work across both; structured signals (contradiction, action tracking, skill drift) degrade gracefully to schema-1-only. Accepted trade-off: reflect simplicity > dream signal richness. |
| Reads `<repo>/.claude/memory/` not `~/.claude/projects/*/memory/` | The latter is Conductor's auto-memory and is wiped on workspace rotation. |
| Scoring criteria duplicated from /reflect Step 3 | Intentional: skills must be self-contained; cross-skill references to prose sections break if the source skill is renamed or restructured. |
| Checklist pruning in /dream, not /review-loop | /review-loop only has single-session visibility; /dream has the cross-session data needed to judge whether an item is genuinely stale vs. just not triggered recently. |
