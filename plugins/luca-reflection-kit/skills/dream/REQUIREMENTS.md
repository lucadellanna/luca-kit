# Requirements

## Purpose

Surface multi-session patterns that single-session reflection cannot see, and help the user prune or consolidate the rule corpus accordingly.

## Required outcomes

1. Surfaces patterns visible only across sessions (not within one).
2. Each surfaced item carries a specific proposed action.
3. The user evaluates and confirms each action before any file is modified.
4. Items the user has previously declined are not re-surfaced unless new evidence has accrued since the decline.

## Required signals to detect (from /reflect logs)

5. Concepts that recur across multiple sessions.
6. Concepts the user has repeatedly declined.
7. Rules that did not prevent recurrence of the issue they targeted.
8. Memory entries that contradict each other.
9. Skills receiving repeated, inconsistent edit proposals (drift).

## Required signals when optional sources are present

10. Patterns in `~/.claude/error-log.md` when the file exists: recurring error classes, and structural fixes proposed but not landed.
11. Hygiene issues in `~/.claude/code-review-checklist.md` when the file exists: stale items and duplicates.
12. When any optional source is absent, the skill proceeds silently without it.

## Constraints

13. Multi-session analysis covers the current project only.
14. Reads and writes are limited to the user's `~/.claude/` tree and the current project's rule files. No workspace-local artifacts.
15. Reads existing reflect log entries regardless of their schema version. Unknown schemas are silently skipped.
16. Token-efficient on large logs: does not load multi-MB content into LLM context without user opt-in.
17. Caps surfaced items so the output remains scannable.
18. Surface ranking reflects likely impact.

## Non-goals (excluded from v1)

19. Cross-project / cross-repo analysis. Deferred to v2; data sparsity makes it unreliable until then.
20. Telemetry-based rule-effectiveness measurement. No firing data exists.
21. Detection of stale-but-silent rules. Indistinguishable from working-as-intended without firing telemetry.
22. Detection of verbosity or token-use trends through per-session aggregates. Requires extending /reflect's logger; deferred.
23. Automatic application of any change.
24. Code or source-file analysis.

---

# Scoring criteria

Each criterion is scored 0 to 10. Target average ≥ 9.5. Below threshold, revise and re-score; cap at 3 iterations.

## Conciseness

Every requirement earns its place. Removing it would weaken what the implementation can be evaluated against, or would create silent ambiguity. No restatement of the same property in two places.

- 10 : every requirement is load-bearing.
- 7 : one or two requirements could be merged or removed without losing evaluative power.
- 4 : visible duplication, or items that are design/process leaking in.
- 0 : largely redundant or implementation-bound.

## Runtime efficiency

The required behavior, when implemented as written, can be delivered without wasted reads, redundant agent calls, or unnecessary context loads.

- 10 : the requirements admit an implementation with no avoidable waste.
- 7 : one requirement forces a minor inefficiency without justification.
- 4 : multiple requirements force avoidable redundancy.
- 0 : the requirements are structurally wasteful regardless of implementation.

## Adherence to requirements

This criterion is applied to SKILL.md, not to this file. Every requirement above is implemented exactly. No requirement is silently skipped, partially implemented, or extended beyond what is specified.

- 10 : every requirement is implemented as written; no scope creep, no omissions.
- 7 : one or two minor deviations with no behavioral impact.
- 4 : one substantive requirement skipped or one substantive behavior added that is not in the requirements.
- 0 : multiple requirements unmet or contradicted.
