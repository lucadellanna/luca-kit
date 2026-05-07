---
name: Create Operational Skill
description: Create a reusable Claude skill from a business procedure, SOP, wiki page, checklist, or verbal description of a recurring task. For non-technical teams turning operating knowledge into repeatable AI workflows.
version: 0.1.0
---

# Create Operational Skill

You help non-technical users turn business knowledge into a reusable Claude skill (a SKILL.md file). Speak plainly — no developer jargon.

Steps 1–2 use Haiku (information gathering). Step 3 uses Sonnet (drafting).

## Step 1: Understand the source

Determine what the user has:

- **Source material provided** (SOP, procedure doc, checklist, wiki page, pasted text): Read it. Summarize the task it describes in 2–3 sentences. Ask the user to confirm or correct.
- **No source material**: Ask these questions (first one alone, then the remaining two together once the purpose is clear):
  1. What recurring task should this skill handle?
  2. What does a good result look like?
  3. What should the skill never do?

Keep this step short. Extract only: purpose, key steps, scope boundaries.

Before continuing to the next step, ensure you understand the context and purpose; do not continue until this is fully clear without you having to make assumptions. If you make assumptions, ask the user to validate them.

## Step 2: Define success criteria

Before drafting, agree with the user on 2–5 measurable criteria for scoring the SKILL.md document quality (Step 4). These let Claude score the draft and improve it before saving — the stricter the criteria, the better the final skill. They are separate from the task-performance criteria that will go inside the generated skill.

Default document-quality criteria (adjust based on context):

| # | Criterion |
|---|-----------|
| 1 | Clarity — a new employee could use this without asking questions |
| 2 | Completeness — all essential steps and decision points are covered |
| 3 | Safety — approval points and scope limits are explicit where stakes are non-trivial |
| 4 | Conciseness — the skill document itself is lean: no unnecessary words, steps, or sentences |
| 5 | Runtime efficiency — when run, the skill uses the appropriate model tier (Haiku for simple/fast steps, Sonnet for balanced work, Opus for complex reasoning), spawns sub-agents where they improve quality or speed and avoids them otherwise, and minimises unnecessary back-and-forth or verbose outputs |
| 6 | Self-reflection quality — the generated skill's `## Self-reflection` section has 2–5 criteria that are appropriate (relevant to the skill's purpose) and MECE (no overlap between criteria; together they fully capture "good output") |

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

## Self-reflection

[2–5 MECE success criteria go here.]

Spawn a Haiku sub-agent to score each criterion 0–10. If average < 9.5, revise and re-score. Stop after 3 iterations or if the score stops improving. If any criterion remains below 8 after iteration, draft a concise edit to this SKILL.md to prevent the same failure, show it to the user, and apply on approval.

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
- Never write CLI commands, install steps, or configuration syntax you're not certain is correct — flag uncertainty and ask whether to verify or omit.
- Include a `## Self-reflection` section with 2–5 MECE success criteria and the standard loop (see CLAUDE.md).
- Include a `## Design decisions` table — document intentional trade-offs so future audits don't penalise accepted choices. Leave the placeholder row if no decisions exist yet.

## Step 4: Score and iterate this SKILL.md draft

This step scores the SKILL.md *document quality* against the criteria agreed in Step 2. The generated skill's *runtime quality* is evaluated separately in `## Self-reflection` at the end.

Spawn a Haiku sub-agent to score the draft. Pass it:
1. The full SKILL.md draft text
2. The agreed criteria and their definitions
3. The instruction: "Score each criterion 0–10. If the draft has a ## Design decisions section, score net of documented decisions — do not penalise intentional trade-offs. For each criterion, give a one-sentence rationale and name the specific element that most affected the score. Return a markdown table."

Use the sub-agent's scores directly:

| Criterion | Score | Gap |
|-----------|-------|-----|
| [Criterion Name] | X/10 | [what's missing] |

- If average ≥ 9.5: proceed to Step 5.
- If average < 9.5: revise the draft to close the lowest-scoring gaps. Re-score. Repeat.
- If the average did not improve from the previous iteration: stop iterating, proceed to Step 5 with the best version.

Do not iterate more than 3 times.

## Step 5: Code-level correctness review

Spawn a `feature-dev:code-reviewer` sub-agent. Pass it the full SKILL.md text and this prompt:

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

Apply any fixes to the draft before proceeding. If the sub-agent is unavailable, skip and note "code-reviewer not available — skipping correctness check."

## Step 6: Confirm and save

Show the user the final SKILL.md. Ask for explicit approval before writing the file.

On approval: create the directory `skills/<skill-name>/` and write the content to `skills/<skill-name>/SKILL.md`.

## Step 7: Audit the new skill

Open an `audit-skill` session and provide the absolute path to the saved skill file in the opening message. Resolve it first: run `realpath skills/<skill-name>/SKILL.md` via Bash and use that output. If `audit-skill` is unavailable, note "audit-skill not found; skipping quality audit." and continue to Self-reflection.

## Self-reflection

Spawn a Haiku sub-agent to verify the runtime quality of the skill just saved (distinct from the document quality checked in Step 4):

1. **Usefulness** — The generated skill would let a new user complete the task without asking for help
2. **Efficiency** — No unnecessary questions were asked; the user wasn't asked to make decisions that Claude could make
3. **Coverage** — the generated skill covers all key steps and decision points from the source material

If any criterion scores below 8, draft a concise edit to this SKILL.md to prevent the same failure, show it to the user, and apply on approval.

## Design decisions

| Decision | Rationale |
|----------|-----------|
| 6 default criteria in Step 2 (exceeds the 2–5 guideline) | Defaults are a menu, not a mandate — users confirm and trim to 2–5 in the Step 2 conversation; a richer starting menu produces better criteria choices than a shorter one |
| Haiku sub-agent for scoring in Step 4 | CLAUDE.md-mandated pattern — reduces confirmation bias; apparent overhead is intentional |
| code-reviewer runs before save (Step 5) | Catches injection, boundary, redundant-state, and contradiction bugs that prose-level review misses; placed before save so the user approves the technically verified version |
| audit-skill runs after save (Step 7) | Skills start life with a quality score rather than waiting for a future audit-skills rotation; co-installed as part of the same plugin so almost always available |
