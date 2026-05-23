# Design decisions

| Decision | Rationale |
|----------|-----------|
| Invoke `luca-kit:list-skills` in raw mode rather than embedding its script | Single source of truth for the data-collection script; raw mode is the DRY interface for skills that need structured data |
| Overlap detection runs every session | The skill library can change between runs; re-scanning is cheap relative to missing a new duplicate |
| No sub-agent for Step 2 (overlap scan) | ~76 TSV rows and lightweight semantic judgment; dispatching a sub-agent adds latency with no quality gain |
| Semantic judgment for description overlap, not string similarity | Skill descriptions are short and human-authored; Claude's semantic read is more reliable than word-overlap heuristics at this scale |
| `next_audit_path` advances by `batch_size`, not by confirmed count | Keeps cycle progress predictable; skipped skills return in the next rotation. Advancing by confirmed count would re-present already-audited skills when the cursor wraps |
| State stores only `next_audit_path`, not `skills_order` + cursor | `skills_order` is redundant (`luca-kit:list-skills` always returns the current list); storing the full list creates a synchronization problem. A single path is the minimal stable anchor: unique across scopes, unambiguous after reconciliation |
| Wrap message deferred to Step 6 | Firing it in Step 3 (before confirmation) would tell the user "cycle complete" before they've reviewed anything this session |
| `audit-skill` invoked as a sequential interactive session | `audit-skill` calls `AskUserQuestion` for improvement approvals; silently batching would violate the human-approval principle |
| Default batch size = 3 | Enough progress per session; small enough not to exhaust token budget on auditing alone |
| State file at `.claude/audit-skills-state.json` | Project-local; `.claude/` is the established container for project-level Claude metadata |
| Wrap flag fires even when `start_index = 0` | When `batch_size >= total_skills`, every session covers all skills; `start_index` is always 0 but the cycle genuinely completes each run. Guarding with `start_index > 0` would permanently silence the message for small libraries. |
| 6 self-reflection criteria (exceeds project norm of 2–5) | All 6 are genuinely distinct and collectively exhaustive for this multi-step orchestration skill; merging any two would lose precision |
