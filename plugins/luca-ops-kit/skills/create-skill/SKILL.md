---
name: Create Operational Skill
description: Create a reusable Claude skill from a business procedure, SOP, wiki page, checklist, or verbal description of a recurring task. For non-technical teams turning operating knowledge into repeatable AI workflows.
version: 0.2.0
---

# Create Operational Skill

You help non-technical users turn business knowledge into a reusable Claude skill (a SKILL.md file). Speak plainly; no developer jargon.

Steps 1–2 use Haiku (information gathering). Step 3 uses Sonnet (drafting).

## Step 1: Understand the source

Determine what the user has:

- **Source material provided** (SOP, procedure doc, checklist, wiki page, pasted text): Read it. Summarize the task it describes in 2–3 sentences. Use AskUserQuestion (open text) to ask the user to confirm or correct.
- **No source material**: Use AskUserQuestion (open text) for each of these questions (ask the first one alone, then the remaining four together once the purpose is clear):
  1. What recurring task should this skill handle?
  2. What does a good result look like?
  3. What should the skill never do?
  4. Who will run this skill? (e.g., manager, admin, salesperson)
  5. What usually triggers it -- a specific event, a request from someone, a schedule?

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
| 8 | Design decision coverage: every intentional trade-off or non-obvious constraint has a row in `DESIGN.md`; a reviewer seeing the skill cold should not flag an intentional choice as a gap |

Present defaults. Use AskUserQuestion (open text) to ask the user to confirm, modify, or add criteria. Move on once agreed.

## Step 3: Present skill blueprint in plan mode

Synthesize from Steps 1–2 into a structured blueprint before drafting anything:

- **Skill name**: proposed kebab-case verb-noun directory name
- **Purpose**: one sentence
- **Step outline**: 3–7 numbered steps, high-level only (no sub-steps)
- **Human approval gates**: any steps that require explicit user confirmation before acting
- **Out of scope**: what this skill will not do
- **Success criteria**: the agreed list from Step 2 (one line each)

Call EnterPlanMode. Present the blueprint in a single formatted markdown block. Tell the user: "Review this plan. Approve to begin drafting, or tell me what to change."

Stay in plan mode until the user approves. If corrections are given, update the blueprint and re-present before asking for approval again. Once approved, call ExitPlanMode, then proceed to Step 4.

## Step 4: Draft the skill

Write a SKILL.md file with this structure:

```
---
name: [Skill Name]
description: [One line: when should this skill activate?]
version: 0.1.0
---

[Body: purpose, steps, decision points, approval gates, scope boundaries]

## Self-reflection

During execution, follow the self-observation protocol (see CLAUDE.md Principles).

[2–5 MECE success criteria go here.]

Spawn a Haiku sub-agent to score each criterion 0–10. If average < 9.5, revise the output and re-score. Stop after 3 iterations or if the score stops improving. If any criterion remains below 8 after iteration, draft a concise edit to this SKILL.md to prevent the same failure, show it to the user, and use Edit to apply it on approval.
```

Also draft a `DESIGN.md` alongside `SKILL.md`:

```
# Design decisions

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
- Include a `## Self-reflection` section with the self-observation protocol one-liner, 2–5 MECE success criteria, and the standard loop (see CLAUDE.md).
- Create a separate `DESIGN.md` file alongside `SKILL.md` with a `# Design decisions` table; document intentional trade-offs there so future audits don't penalise accepted choices. Leave the placeholder row if no decisions exist yet.

## Step 5: Score and iterate this SKILL.md draft

This step scores the SKILL.md *document quality* against the criteria agreed in Step 2. The generated skill's *runtime quality* is evaluated separately in `## Self-reflection` at the end.

Spawn a Sonnet sub-agent to score the draft. Pass it:
1. The full SKILL.md draft text
2. The DESIGN.md draft text
3. The agreed criteria and their definitions
4. The instruction: "FIRST: review the design decisions provided and list each one. Then, for each criterion below, if a concern you would raise is already listed there as an intentional trade-off, do not reduce the score for it. Score each criterion 0–10. For each, give a one-sentence rationale and name the specific element that most affected the score. Return a markdown table, no preamble."

Use the sub-agent's scores directly:

| Criterion | Score | Gap |
|-----------|-------|-----|
| [Criterion Name] | X/10 | [what's missing] |

- If average ≥ 9.5: proceed to Step 6.
- If average < 9.5: revise the draft to close the lowest-scoring gaps. Spawn a fresh Sonnet sub-agent passing the revised draft, the agreed criteria, and the same instruction string from above. Repeat.
- If the average did not improve from the previous iteration: stop iterating, proceed to Step 6 with the best version.

Do not iterate more than 3 times.

## Step 6: Code-level correctness review

Spawn a `feature-dev:code-reviewer` sub-agent. Pass it the full SKILL.md text, the DESIGN.md text, and this prompt:

> Treat this SKILL.md as executable code. Check:
> (a) Data format fields: are any TSV/JSON fields susceptible to delimiter or newline injection that would corrupt a consuming skill?
> (b) Algorithm edge cases at boundaries: empty list, total items < batch size, deleted item at cursor position.
> (c) Redundant state: variables or flags that are set but never used, or derived values that are recomputed unnecessarily.
> (d) Logical contradictions: sentences within the same step that give conflicting instructions.
> (e) Implicit formats: any reference to "today", "current date", or "now" without specifying the exact format or the bash command to produce it (e.g. `date +%Y-%m-%d`).
> (f) Undefined variables: any variable used in a formula or condition that is not explicitly defined earlier in the same step.
> (g) Inter-process output headers: if the skill consumes output from another skill or script, does it account for header/metadata lines that are not data rows?
> (h) Relative paths passed between skills: any path handed to another skill as data must be absolute; flag any that aren't.
> (i) Duplicate instructions: the same rule or fact stated in two places; flag so one can be removed to prevent drift.
> (j) Approval gate ordering: steps that write files, send messages, or perform irreversible external actions must appear after all automated review and correction steps, not before.
>
> For each issue found, quote the offending text and propose a minimal fix. If no issues are found, say so explicitly.

Apply any fixes to the draft before proceeding. If the sub-agent is unavailable, skip and note "code-reviewer not available; skipping correctness check."

## Step 7: Confirm and save

Show the user the final SKILL.md. Use AskUserQuestion (open text) to ask for explicit approval before writing the file.

On approval: use Bash to create the directory `skills/<skill-name>/`, then use Write to save `skills/<skill-name>/SKILL.md` and `skills/<skill-name>/DESIGN.md`.

## Step 8: Audit the new skill

Open an `audit-skill` session and provide the absolute path to the saved skill file in the opening message. Resolve it first: run `realpath skills/<skill-name>/SKILL.md` via Bash and use that output. If `audit-skill` is unavailable, note "audit-skill not found; skipping quality audit." and continue to Self-reflection.

## Step 9: Update project documentation

Use Read to check whether `README.md` and `CLAUDE.md` exist at the project root. For each file that exists, scan its content for a skills section: a `## Skills` heading, a Markdown table with a "Skill" column header, or a bullet list of skill names. If neither file contains a skills section, skip this step silently.

For each file that has a skills section, propose adding the new skill using its frontmatter `name` and `description` fields. Show the exact text that would be inserted (matching the surrounding format (table row or bullet line)).

Use AskUserQuestion (multiSelect: true, pre-select all candidates):
> "I found a skills list in [file(s)]. Add the new skill there?"

For each confirmed file, use Edit to insert the entry into the existing table or list. Do not create a new section; only append to existing ones.

## Self-reflection

During execution, follow the self-observation protocol (see CLAUDE.md Principles).

Spawn a Haiku sub-agent to verify the runtime quality of the skill just saved (distinct from the document quality checked in Step 5). Pass it the generated SKILL.md content and the source material from Step 1, with the instruction: "Score each criterion 0–10. For each, give a one-sentence rationale. Return a markdown table, no preamble."

1. **Usefulness**: the generated skill would let a new user complete the task without asking for help
2. **Efficiency**: no unnecessary questions were asked; the user wasn't asked to make decisions that Claude could make
3. **Coverage**: the generated skill covers all key steps and decision points from the source material

If any criterion scores below 8, draft a concise edit to this SKILL.md to prevent the same failure, show it to the user, and use Edit to apply it on approval.

