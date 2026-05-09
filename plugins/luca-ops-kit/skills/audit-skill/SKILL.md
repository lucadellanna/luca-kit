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
| 1 | **Clarity & conciseness** | The skill's user-facing messages (what Claude says and asks during execution) are in plain language a non-technical user can act on without follow-up questions. SKILL.md technical content (code blocks, tool names, model tier directives, sub-agent spawns) is instruction for Claude to execute, not content shown to users; do not penalise it for non-technical readability. Length: nothing longer than needed. |
| 2 | **Context discipline** | Asks clarifying questions before acting on incomplete or unvalidated context. Never assumes the user's situation or intent. |
| 3 | **Security** | Every action with real-world consequences (file writes, sends, deletes, external calls) requires explicit user approval before proceeding. |
| 4 | **Token efficiency** | Two sub-dimensions: (a) *document*: the SKILL.md text is lean, no redundant words or boilerplate; (b) *runtime*: the skill uses the appropriate model tier (Haiku for simple/fast steps, Sonnet for balanced work, Opus for complex reasoning), spawns sub-agents where they improve quality or speed and avoids them otherwise, and minimises unnecessary back-and-forth or verbose outputs. |
| 5 | **Effectiveness** | Has a `## Self-reflection` section with the self-observation protocol reference and 2–5 criteria. Score on how *appropriate* (relevant to the skill's purpose) and *MECE* (mutually exclusive: no overlap; collectively exhaustive: together they fully capture "good output" for this skill) the criteria are. No section = 0. Missing self-observation reference or wrong/overlapping criteria = low. |
| 6 | **Instruction explicitness** | Every action the skill instructs Claude to perform names the specific tool to use and the expected outcome, not just the goal. "Use Read to check if X exists; if the file is not found, proceed to Y" rather than "Check if X exists." Implied tool choices, ambiguous outcomes, or steps that assume Claude will infer the mechanism score low. |
| 7 | **Design decision coverage** | Every intentional trade-off, non-obvious constraint, or deliberate limitation has a row in `## Design decisions`. A reviewer seeing the skill cold should not be able to flag an intentional choice as a gap. Missing section = 0. Section exists but omits obvious choices = low. |

## Step 1: Identify the target

If no skill path was provided, ask which skill to audit. Read the file. If it doesn't exist, say so and stop.

## Step 2: Score (initial)

Spawn a Sonnet sub-agent to score the skill. Pass it:
1. The full SKILL.md content
2. The scoring criteria from the **Scoring criteria** section above
3. The instruction: "FIRST: read the ## Design decisions section and list every documented decision. Then, for each criterion below, if a concern you would raise is already listed there as an intentional trade-off, do not reduce the score for it. Score each criterion 0–10. For each, give a one-sentence rationale and name the specific line or gap that most affected the score. Return a markdown table; no preamble."

Use the sub-agent's scores directly:

| Criterion | Score | Rationale & key gap |
|-----------|-------|---------------------|
| Clarity & conciseness | X/10 | |
| Context discipline | X/10 | |
| Security | X/10 | |
| Token efficiency | X/10 | |
| Effectiveness | X/10 | |
| Instruction explicitness | X/10 | |
| Design decision coverage | X/10 | |
| **Average** | **X/10** | |

## Step 3: Brainstorm improvements

List every potential improvement in one sentence each. Cover:

- Gap fixes from Step 2
- Novel opportunities (edge cases, interaction patterns, structural improvements not visible from the scores)
- **Mandatory:** if no `## Self-reflection` section exists, adding one is always an improvement. If the section exists but lacks the self-observation protocol reference, adding it is always an improvement.

For each item, mark it as one of:
- **Fix**: genuine bug, missing safety control, or clear UX failure; requires a code change
- **Document**: inherent trade-off, accepted limitation, or concern that requires extraordinary user action to trigger; the correct response is a Design decisions entry, not a code change
- **Skip**: low impact or out of scope

Don't filter yet.

## Step 4: Prioritize

Show only **Fix** and **Document** items (drop **Skip**), numbered. Present them in two groups: "Code fixes" and "Design decisions to add."

Use AskUserQuestion (multiSelect: true) with each item as an option, all pre-selected by default. Ask: "Which improvements should I apply?" If items exceed 4, split into multiple consecutive AskUserQuestion calls (max 4 per call). Aggregate all selected items and proceed only with those.

## Step 5: Apply

For each selected **Fix** item: state the planned edit in one line, then use Edit to apply it.
For each selected **Document** item: add a row to `## Design decisions` explaining the trade-off. Do not write code changes for Document items.

## Step 6: Re-score and iterate

Spawn a fresh Sonnet sub-agent to re-score. Pass it the updated skill file content and the scoring criteria from the **Scoring criteria** section above, with the instruction: "FIRST: read the ## Design decisions section and list every documented decision. Then, for each criterion below, if a concern you would raise is already listed there as an intentional trade-off, do not reduce the score for it. Score each criterion 0–10. For each, give a one-sentence rationale and name the specific line or gap that most affected the score. Return a markdown table; no preamble."

- Average ≥ 9.5 → proceed to Step 7.
- Score increased by < 0.5 and all applied changes were objectively positive (additions or tightening only, no substantive content removed) → treat as scoring variance; stop and proceed to Step 7 with the current version.
- Average < 9.5 and higher than the previous iteration → return to Step 3. Do not re-apply changes already made.
- Score declined or no improvement for any other reason → stop, proceed to Step 7 with the best version reached.

Maximum 3 total iterations.

## Step 7: Final summary

Present:

1. Final score table
2. 1–2 sentence summary of what changed and what remains below threshold (if anything)

## Self-reflection

During execution, follow the self-observation protocol (see CLAUDE.md Principles).

Spawn a Haiku sub-agent to verify the audit's own quality on these criteria:

1. **Score improved**: the audited skill's final average is higher than its initial score, OR the initial score was already ≥ 9.5, OR the user declined all proposed improvements, OR all user-confirmed improvements were applied and the score stagnated (genuine edits that don't move the score are not audit failures)
2. **All confirmed items applied**: no user-confirmed improvement was skipped
3. **No regressions**: criteria that scored well initially are not worse in the final version; re-scoring variance of < 0.5 points on an unedited criterion does not count as a regression

If any criterion scores below 8, draft a concise edit to this SKILL.md to prevent the same failure, show it to the user, and apply on approval.

## Design decisions

| Decision | Rationale |
|----------|-----------|
| Criteria table passed to sub-agents in full on each call | Stateless sub-agents have no access to the parent conversation; full context must be provided on every spawn; this is not redundancy |
| No edit-permission check in Step 1 | Skills live in team-owned repositories; the caller is assumed to have appropriate access |
| Sonnet (not Haiku) for scoring sub-agents | Instruction explicitness and criterion ambiguity require simulating execution paths; Haiku scores surface-level clarity but misses subtle precision gaps. Haiku remains appropriate for the self-reflection binary checks. |
| Fix vs. Document classification in Step 3 | Concerns that are inherent trade-offs should become Design decisions entries, not code changes; conflating the two causes wasted iteration rounds where the re-scorer flags the same concern again because it isn't yet documented |
| Clarity criterion scoped to user-facing outputs, not SKILL.md text | SKILL.md contains technical instructions for Claude (code blocks, tool names, model directives); penalising these for non-technical readability misapplies the criterion; Token efficiency already judges SKILL.md text length |
| Design-decision pre-check is a mandatory first step in scorer prompt | Placing "score net of documented decisions" as a trailing clause in prose causes scorers to acknowledge it in aggregate but ignore it per-criterion; making it the first explicit step anchors the scorer before any criterion is evaluated |
