---
name: Audit Skill
description: Use when asked to audit, review, or improve an existing skill file. Scores it on 5 quality dimensions, brainstorms and applies improvements, then iterates until the quality bar is met.
version: 0.1.0
---

# Audit Skill

Score an existing skill, improve it, and iterate until it meets quality standards.

## Scoring criteria

| # | Criterion | What earns a 10 |
|---|-----------|----------------|
| 1 | **Clarity & conciseness** | Plain language, short sentences; a non-technical user can follow without asking questions. Nothing longer than needed. |
| 2 | **Context discipline** | Asks clarifying questions before acting on incomplete or unvalidated context. Never assumes the user's situation or intent. |
| 3 | **Security** | Every action with real-world consequences (file writes, sends, deletes, external calls) requires explicit user approval before proceeding. |
| 4 | **Token efficiency** | Two sub-dimensions: (a) *document* — the SKILL.md text is lean, no redundant words or boilerplate; (b) *runtime* — the skill uses the appropriate model tier (Haiku for simple/fast steps, Sonnet for balanced work, Opus for complex reasoning), spawns sub-agents where they improve quality or speed and avoids them otherwise, and minimises unnecessary back-and-forth or verbose outputs. |
| 5 | **Effectiveness** | Has a `## Self-reflection` section with 2–5 criteria. Score on how *appropriate* (relevant to the skill's purpose) and *MECE* (mutually exclusive — no overlap; collectively exhaustive — together they fully capture "good output" for this skill) the criteria are. No section = 0. Section with wrong or overlapping criteria = low. |

## Step 1: Identify the target

If no skill path was provided, ask which skill to audit. Read the file. If it doesn't exist, say so and stop.

## Step 2: Score (initial)

Spawn a Haiku sub-agent to score the skill. Pass it:
1. The full SKILL.md content
2. The scoring criteria from the **Scoring criteria** section above
3. The instruction: "Score each criterion 0–10. If the skill has a ## Design decisions section, score net of documented decisions — do not penalise intentional trade-offs. For each criterion, give a one-sentence rationale and name the specific line or gap that most affected the score. Return a markdown table — no preamble."

Use the sub-agent's scores directly:

| Criterion | Score | Rationale & key gap |
|-----------|-------|---------------------|
| Clarity & conciseness | X/10 | |
| Context discipline | X/10 | |
| Security | X/10 | |
| Token efficiency | X/10 | |
| Effectiveness | X/10 | |
| **Average** | **X/10** | |

## Step 3: Brainstorm improvements

List every potential improvement in one sentence each. Cover:

- Gap fixes from Step 2
- Novel opportunities (edge cases, interaction patterns, structural improvements not visible from the scores)
- **Mandatory:** if no `## Self-reflection` section exists, adding one is always an improvement

Don't filter yet.

## Step 4: Prioritize

Label each item **Act** (high impact, within the skill's scope) or **Skip** (low impact or out of scope). Show only **Act** items, numbered.

Use AskUserQuestion (multiSelect: true) with each Act item as an option, all pre-selected by default. Ask: "Which improvements should I apply?" If Act items exceed 4, split them into multiple consecutive AskUserQuestion calls (max 4 items per call). Aggregate all selected items and proceed only with those.

## Step 5: Apply

State each planned edit in one line, then apply it.

## Step 6: Re-score and iterate

Spawn a fresh Haiku sub-agent to re-score. Pass it the updated skill file content and the scoring criteria from the **Scoring criteria** section above, with the instruction: "If the skill has a ## Design decisions section, score net of documented decisions — do not penalise intentional trade-offs."

- Average ≥ 9.5 → proceed to Step 7.
- Score increased by < 0.5 and all applied changes were objectively positive (additions or tightening only, no substantive content removed) → treat as Haiku variance; stop and proceed to Step 7 with the current version.
- Average < 9.5 and higher than the previous iteration → return to Step 3. Do not re-apply changes already made.
- Score declined or no improvement for any other reason → stop, proceed to Step 7 with the best version reached.

Maximum 3 total iterations.

## Step 7: Final summary

Present:

1. Final score table
2. 1–2 sentence summary of what changed and what remains below threshold (if anything)

## Self-reflection

Spawn a Haiku sub-agent to verify the audit's own quality on these criteria:

1. **Score improved** — the audited skill's final average is higher than its initial score, OR the initial score was already ≥ 9.5, OR the user declined all proposed improvements
2. **All confirmed items applied** — no user-confirmed improvement was skipped
3. **No regressions** — criteria that scored well initially are not worse in the final version

If any criterion scores below 8, draft a concise edit to this SKILL.md to prevent the same failure, show it to the user, and apply on approval.

## Design decisions

| Decision | Rationale |
|----------|-----------|
| Criteria table passed to sub-agents in full on each call | Stateless sub-agents have no access to the parent conversation; full context must be provided on every spawn — this is not redundancy |
| No edit-permission check in Step 1 | Skills live in team-owned repositories; the caller is assumed to have appropriate access |
