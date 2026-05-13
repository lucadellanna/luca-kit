# Quality requirements

This skill must satisfy the following, scored 0 to 10 each, average >= 9.5:

## Baseline (always)
- **Conciseness**: every sentence, step, and section earns its place; removing anything would not change the outcome.
- **Runtime efficiency**: no anti-patterns from the luca-ops-kit `runtime-efficiency` checklist apply.
- **Simplicity**: no step, loop, sub-agent, or file exists unless its absence would produce a worse outcome.

## Ad-hoc (specific to this skill)
- **Clarity (Claude as executor)**: every step and the subagent prompt template is unambiguous; no step requires the executor to make a judgment call about format or contract.
- **Design decision coverage**: every intentional trade-off (derivation locus, single-file scope, `FINDINGS:` marker, re-spawn budget, uniqueness pre-flight, adjacent-edit handling) has a row in `DESIGN.md`.
- **Self-reflection quality**: the 5 self-reflection criteria are MECE, appropriate to the skill's purpose, and each is independently scorable 0 to 10 from the artifacts the scorer receives.
