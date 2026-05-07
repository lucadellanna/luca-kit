---
name: Create Operational Skill
description: Create a reusable Claude skill from a business procedure, SOP, wiki page, checklist, or verbal description of a recurring task. For non-technical teams turning operating knowledge into repeatable AI workflows.
version: 0.1.0
---

# Create Operational Skill

You help non-technical users turn business knowledge into a reusable Claude skill (a SKILL.md file). Speak plainly; no developer jargon.

Steps 1–2 use Haiku (information gathering). Step 3 uses Sonnet (drafting).

## Step 1: Understand the source

Determine what the user has:

- **Source material provided** (SOP, procedure doc, checklist, wiki page, pasted text): Read it. Summarize the task it describes in 2–3 sentences. Use AskUserQuestion (open text) to ask the user to confirm or correct.
- **No source material**: Use AskUserQuestion (open text) for each of these questions (ask the first one alone, then the remaining two together once the purpose is clear):
  1. What recurring task should this skill handle?
  2. What does a good result look like?
  3. What should the skill never do?

Keep this step short. Extract only: purpose, key steps, scope boundaries.

Before continuing to the next step, ensure you understand the context and purpose; do not continue until this is fully clear without you having to make assumptions. If you make assumptions, ask the user to validate them.

## Step 2: Define success criteria

Before drafting, agree with the user on 2–5 measurable criteria for scoring the SKILL.md document quality (Step 4). These let Claude score the draft and improve it before saving; the stricter the criteria, the better the final skill. They are separate from the task-performance criteria that will go inside the generated skill.

Default document-quality criteria (adjust based on context):

| # | Criterion |
|---|-----------|
| 1 | Clarity: a new employee could use this without asking questions |
| 2 | Completeness: all essential steps and decision points are covered |
| 3 | Safety: approval points and scope limits are explicit where stakes are non-trivial |
| 4 | Conciseness: the skill document itself is lean; no unnecessary words, steps, or sentences |
| 5 | Runtime efficiency: when run, the skill uses the appropriate model tier (Haiku for simple/fast steps, Sonnet for balanced work, Opus for complex reasoning), spawns sub-agents where they improve quality or speed and avoids them otherwise, and minimises unnecessary back-and-forth or verbose outputs |
| 6 | Self-reflection quality: the generated skill's `## Self-reflection` section has 2–5 criteria that are appropriate (relevant to the skill's purpose) and MECE (no overlap between criteria; together they fully capture "good output") |
| 7 | Instruction explicitness: every action names the specific tool to use and the expected outcome, not just the goal (e.g., "Use Read to open X; if not found, proceed to Y" rather than "Check if X exists") |
| 8 | Design decision coverage: every intentional trade-off or non-obvious constraint has a row in `## Design decisions`; a reviewer seeing the skill cold should not flag an intentional choice as a gap |

Present defaults. Use AskUserQuestion (open text) to ask the user to confirm, modify, or add criteria. Move on once agreed.

## Step 3: Draft the skill

Write a SKILL.md file with this structure:

```
---
name: [Skill Name]
description: [One line: when should this skill activate?]
version: 0.1.0
---

[Body: purpose, steps, decision points, approval gates, scope boundaries]

## Self-reflection

[2–5 MECE success criteria go here.]

Spawn a Haiku sub-agent to score each criterion 0–10. If average < 9.5, revise the output and re-score. Stop after 3 iterations or if the score stops improving. If any criterion remains below 8 after iteration, draft a concise edit to this SKILL.md to prevent the same failure, show it to the user, and use Edit to apply it on approval.

## Design decisions

| Decision | Rationale |
|----------|-----------|
| [Intentional trade-off] | [Why it was accepted] |
```

Rules for the draft:
- Plain language. Short sentences.
- Steps, not paragraphs. Use numbered lists for sequences, tables for decision logic.
- Include human-approval checkpoints before any action with real-world consequences.
- State what the skill does NOT cover.
- No boilerplate, filler, or examples the user didn't ask for.
- Name the skill directory as kebab-case verb-noun (e.g., `review-invoice`, `onboard-client`).
- Never write CLI commands, install steps, or configuration syntax you're not certain is correct; flag uncertainty and ask whether to verify or omit.
- Include a `## Self-reflection` section with 2–5 MECE success criteria and the standard loop (see CLAUDE.md).
- Include a `## Design decisions` table; document intentional trade-offs so future audits don't penalise accepted choices. Leave the placeholder row if no decisions exist yet.

## Step 4: Score and iterate this SKILL.md draft

This step scores the SKILL.md *document quality* against the criteria agreed in Step 2. The generated skill's *runtime quality* is evaluated separately in `## Self-reflection` at the end.

Spawn a Sonnet sub-agent to score the draft. Pass it:
1. The full SKILL.md draft text
2. The agreed criteria and their definitions
3. The instruction: "Score each criterion 0–10. If the draft has a ## Design decisions section, score net of documented decisions; do not penalise intentional trade-offs. For each criterion, give a one-sentence rationale and name the specific element that most affected the score. Return a markdown table, no preamble."

Use the sub-agent's scores directly:

| Criterion | Score | Gap |
|-----------|-------|-----|
| [Criterion Name] | X/10 | [what's missing] |

- If average ≥ 9.5: proceed to Step 5.
- If average < 9.5: revise the draft to close the lowest-scoring gaps. Spawn a fresh Haiku sub-agent passing the revised draft, the agreed criteria, and the same instruction string from above. Repeat.
- If the average did not improve from the previous iteration: stop iterating, proceed to Step 5 with the best version.

Do not iterate more than 3 times.

## Step 5: Confirm and save

Show the user the final SKILL.md. Use AskUserQuestion (open text) to ask for explicit approval before writing the file.

On approval: use Bash to create the directory `skills/<skill-name>/`, then use Write to save the content to `skills/<skill-name>/SKILL.md`.

## Self-reflection

Spawn a Haiku sub-agent to verify the runtime quality of the skill just saved (distinct from the document quality checked in Step 4). Pass it the generated SKILL.md content and the source material from Step 1, with the instruction: "Score each criterion 0–10. For each, give a one-sentence rationale. Return a markdown table, no preamble."

1. **Usefulness**: the generated skill would let a new user complete the task without asking for help
2. **Efficiency**: no unnecessary questions were asked; the user wasn't asked to make decisions that Claude could make
3. **Coverage**: the generated skill covers all key steps and decision points from the source material

If any criterion scores below 8, draft a concise edit to this SKILL.md to prevent the same failure, show it to the user, and use Edit to apply it on approval.

## Design decisions

| Decision | Rationale |
|----------|-----------|
| 8 default criteria in Step 2 (exceeds the 2–5 guideline) | Defaults are a menu, not a mandate; users confirm and trim to 2–5 in the Step 2 conversation. A richer starting menu produces better criteria choices than a shorter one. |
| Sonnet sub-agent for scoring in Step 4 | Step 2 criteria include instruction explicitness and design decision coverage, which require simulating execution paths; Haiku misses subtle precision gaps in these areas. |
| Self-reflection is one-shot (no average loop) | The self-reflection checks runtime quality of the generated skill, not the document quality of create-skill itself. Document quality is iterated in Step 4. A second loop would conflate the two checks. |
