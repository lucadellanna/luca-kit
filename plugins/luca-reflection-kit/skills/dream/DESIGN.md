# Design decisions

Only non-obvious decisions or ones a future reader might want to revisit. Self-evident choices are not listed.

| Decision | Rationale |
|----------|-----------|
| /dream has its own log, separate from /reflect's | Serves a use case nothing else covers: suppressing previously-rejected candidates from re-surfacing every run. Not a Redundant-mechanism violation because no other log records /dream's decisions. |
| Always asks; no auto-apply, even for low-risk-looking deletions | Pruning is asymmetric to adding: a wrong addition costs one extra line; a wrong deletion silently removes a load-bearing rule. The cost of asking is one extra second; the cost of a wrong silent prune is open-ended. |
| Numbered list + free-form numeric reply, not AskUserQuestion | AskUserQuestion has a hard 4-option cap; /dream regularly surfaces more. Free-form `1 2 4`, `all`, `none`, ranges, removes the cap without losing structure. |
| Inline LLM analysis, not a dedicated sub-agent | The candidate-to-action translation is one focused task. A dedicated sub-agent would add prompt-loading overhead and an extra file for no separation-of-concerns gain. The orchestrator is already an LLM; it does the analysis directly. |
| Schemas 1, 2, 3 normalized at the load layer only | Scattering schema branching through detection logic was the previous design's biggest source of bugs. One migration point (`migrate-log.py`); the rest of the skill sees one shape. |
| Optional sources auto-detected, silent if absent | Some users maintain `~/.claude/error-log.md` and `~/.claude/code-review-checklist.md`; most do not. Auto-detect makes /dream useful to both groups without a flag or mode. |
| Pre-flight log size check (≥ 200 entries or ≥ 5 MB) asks the user | Loading multi-MB of log into LLM context silently is wasteful and opaque. Asking once gives the user the choice between a default 90-day window and processing everything. |
| Recurring concept threshold at ≥ 3 sessions | Two could be coincidence; three is the smallest count that consistently means "this is recurring." Borrowed from the prior /dream and from common pattern-detection heuristics. |
| Stale-insight detection excluded | A silently-working rule (preventing the issue it targets) produces zero recent mentions : identical signal to a stale rule. Without firing telemetry, the two are indistinguishable. Detecting on log-absence would prune working rules. |
| Cross-project / `all` mode deferred to v2 | Cross-repo patterns are real but data-sparse: a concept appearing in two repos out of many is not reliable signal without far more data than current users have. Adds significant complexity for thin v1 value. |
| Per-session aggregates (verbosity, token-use trends) deferred | Requires extending /reflect's logger. Verbosity is partially detectable via the finding text /reflect already surfaces (`"user asked for shorter responses"`); direct measurement waits for a /reflect logger extension. |
| Project memory at `<repo>/.claude/memory/`, not `~/.claude/projects/.../memory/` | The latter is Conductor's auto-memory and is wiped on workspace rotation. Project memory must be checked into the repo to survive. |
| Checklist hygiene lives in /dream, not /review-loop | /review-loop has single-session visibility. /dream has the cross-session data needed to judge whether a checklist item is genuinely stale vs. just untriggered recently. |
