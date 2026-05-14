# Quality requirements

This skill must satisfy the following, scored 0 to 10 each, average >= 9.5:

## Baseline (always)

- **Conciseness**: every sentence, step, and section earns its place; removing anything would not change the outcome.
- **Runtime efficiency**: no anti-patterns from the luca-ops-kit `runtime-efficiency` checklist apply.
- **Simplicity**: no step, loop, sub-agent, or file exists unless its absence would produce a worse outcome.

## Ad-hoc (specific to this skill)

- **Reviewer mandate clarity**: each agent (claude-flow-reviewer, user-flow-reviewer) states unambiguously whose patterns it observes, where its output lands, and what is out of scope. A reader of either agent file alone can produce correctly-shaped output.
- **Mandate-target alignment**: each agent's output target matches its mandate. user-flow recommendations are split by `automatable` so that Claude-side encodings flow through the claude-flow pipeline and user-only items land in the Hint(s) section. claude-flow findings never appear in Hint(s); user-flow output never bypasses the routing.
- **Auto-apply gate strictness**: the four gate criteria (target = `.claude/memory/MEMORY.md`, confidence = high, proposed text <= 2 lines, not a functional duplicate of the rule corpus) are independently checkable; no criterion admits an ambiguous case. The gate never auto-applies to CLAUDE.md, skill files, or other plugins.
- **Quality floor completeness**: each agent file lists all six quality-floor checks (recurrence-or-generalisation, two-whys, value-adding paired test, functional-duplicate rejection, prefer-invoke-existing, mechanism-not-instance) as a mandatory pre-emission filter. No check is missing or implied.
- **Plain language for user-facing output**: Hint(s) recommendations and rationales use plain language. No jargon ("memorialise", "scope re-derivation", "forward-looking opportunity"). A non-technical reader parses each Hint in one read.
- **Design decision coverage**: every intentional trade-off (ledger-vs-digest, auto-apply gate scope, asymmetric reviewer outputs, automatable classification, Hint format, token cost of full rule corpus, source-tree dedup as fallback, plain-language requirement, user-only cap at 3, claude-flow owning user-requirement memorialisation, `tools: []` for pure-reasoning agents, opt-in removed from Step 0) has a row in DESIGN.md.
