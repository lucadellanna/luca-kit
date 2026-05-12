# Quality requirements

This skill must satisfy the following, scored 0–10 each, average ≥ 9.5:

## Baseline (always)
- **Conciseness**: every sentence, step, and section earns its place; removing anything would not change the outcome.
- **Runtime efficiency**: no anti-patterns from `${CLAUDE_PLUGIN_ROOT}/checklists/runtime-efficiency.md` apply.
- **Simplicity**: no step, loop, sub-agent, or file exists unless its absence would produce a worse outcome.

## Ad-hoc (specific to create-skill)
- **Clarity** (for both human readers and Claude as executor): every step is unambiguous; the reader can follow without asking questions.
- **Completeness**: covers source elicitation, overlap check, criteria confirmation, drafting, save (SKILL.md + DESIGN.md + REQUIREMENTS.md + HELP.md), doc-sync, and audit handoff.
- **Safety**: explicit user approval before saving files and before appending to project documentation. (Terminal handoff to `audit-skill` is a read-only quality check and does not require its own approval.)
