---
name: Create Operational Skill
description: Create a reusable Claude skill from a business procedure, SOP, wiki page, checklist, or verbal description of a recurring task. For non-technical teams turning operating knowledge into repeatable AI workflows.
version: 0.1.0
---

# Create Operational Skill

You help non-technical users turn business knowledge into a reusable Claude skill (a SKILL.md file). Speak plainly — no developer jargon.

## Step 1: Understand the source

Determine what the user has:

- **Source material provided** (SOP, procedure doc, checklist, wiki page, pasted text): Read it. Summarize the task it describes in 2–3 sentences. Ask the user to confirm or correct.
- **No source material**: Ask these questions (first one alone, then the remaining two together once purpose is clear):
  1. What recurring task should this skill handle?
  2. What does a good result look like?
  3. What should the skill never do?

Keep this step short. Extract only: purpose, key steps, scope boundaries.

Before continuing to the next step, ensure you understand the context and purpose; do not continue until this is fully clear without you having to make assumptions. If you make assumptions, ask the user to validate them.

## Step 2: Define success criteria

Before drafting, agree with the user on 2–5 measurable criteria for scoring the SKILL.md document quality (Step 4). These are separate from the task-performance criteria that will go inside the generated skill.

Default document-quality criteria (adjust based on context):

| # | Criterion |
|---|-----------|
| 1 | Clarity — a new employee could use this without asking questions |
| 2 | Completeness — all essential steps and decision points are covered |
| 3 | Safety — approval points and scope limits are explicit where stakes are non-trivial |
| 4 | Conciseness — no unnecessary words or steps, no sentence longer than required |
| 5 | Efficiency — no unnecessary token usage, the skill is as efficient as possible to achieve that outcome |

Present defaults. Ask the user to confirm, modify, or add criteria. Move on once agreed.

## Step 3: Draft the skill

Write a SKILL.md file with this structure:

```
---
name: [Skill Name]
description: [One line — when should this skill activate?]
version: 0.1.0
---

[Body: purpose, steps, decision points, approval gates, scope boundaries]

## Score and iterate (include this section in every generated skill)
Generate 2–5 specific success criteria for this skill's runtime output.
Score output 0–10 per criterion. If average < 9.5, revise and re-score.
Stop if score plateaus or after 3 iterations.
```

Rules for the draft:
- Plain language. Short sentences.
- Steps, not paragraphs. Use numbered lists for sequences, tables for decision logic.
- Include human-approval checkpoints before any action with real-world consequences.
- State what the skill does NOT cover.
- No boilerplate, filler, or examples the user didn't ask for.
- Name the skill directory as kebab-case verb-noun (e.g., `review-invoice`, `onboard-client`).
- Never write CLI commands, install steps, or configuration syntax you're not certain is correct — flag uncertainty and ask whether to verify or omit.

## Step 4: Score and iterate this SKILL.md draft

Rate the SKILL.md document you just wrote — not the skill's runtime output — on each agreed criterion:

| Criterion | Score | Gap |
|-----------|-------|-----|
| [Criterion Name] | X/10 | [what's missing] |

- If average ≥ 9.5: proceed to Step 5.
- If average < 9.5: revise the draft to close the lowest-scoring gaps. Re-score. Repeat.
- If the average did not improve from the previous iteration: stop iterating, proceed to Step 5 with the best version.

Do not iterate more than 3 times.

## Step 5: Confirm and save

Show the user the final SKILL.md. Ask for explicit approval before writing the file.

On approval: create the directory `plugins/luca-operating-kit/skills/<skill-name>/` and write the content to `plugins/luca-operating-kit/skills/<skill-name>/SKILL.md`.
