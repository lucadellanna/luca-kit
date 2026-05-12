---
name: create-skill
description: Create a reusable Claude skill from a business procedure, SOP, wiki page, checklist, or verbal description of a recurring task. For non-technical teams, turning operating knowledge into repeatable AI workflows.
version: 0.3.0
---

# Create Operational Skill

You help non-technical users turn business knowledge into a reusable Claude skill. Speak plainly; no developer jargon.

`audit-skill` is the quality gate for the produced skill. This skill produces; `audit-skill` scores. Do not duplicate audit work inline.

## Step 1: Understand the source and prior context

a) **Read the user's saved work context if available.** Use Read on `~/.claude/memory/work-context.md`. If it exists, hold persona, role, decision authority, and customer profile in memory; use them to inform tone and to skip elicitation questions they already answer. If the file is missing, proceed without it. Do not nag the user to set it up.

b) **Note qmd availability.** Use Bash: `test -f ~/.claude/luca-ops-kit/context-search-configured && echo configured || echo not_configured`. If configured, plan to query qmd in sub-step (d) once the purpose is clear.

c) **Read source or elicit.** Determine what the user has:

- **Source material provided** (SOP, checklist, wiki page, pasted text): Read it. Summarize the task it describes in 2–3 sentences. Use AskUserQuestion (open text) to ask the user to confirm or correct.
- **No or insufficient source material**: Use AskUserQuestion (open text) for each question below. Ask question 1 alone, then the remaining four together once the purpose is clear:
  1. What recurring task should this skill handle?
  2. What does a good result look like?
  3. What should the skill never do?
  4. Who will run this skill? (Skip if `work-context.md` already identifies the persona.)
  5. What usually triggers it: a specific event, a request from someone, or a schedule?

d) **If qmd is configured, pull domain context.** Once the purpose is clear, use the qmd MCP `query` tool to search for context relevant to the proposed skill (for an invoice review skill, search "invoice approval"; for a client onboarding skill, search "onboarding checklist"). Surface up to 3 useful snippets to the user before continuing. If nothing relevant returns, skip silently.

Do not proceed until purpose, key steps, and scope are clear without you making assumptions. If you must assume, ask the user to confirm.

## Step 2: Check for overlap with existing skills

Pick 2–4 content keywords from the proposed skill's purpose (verbs and nouns, lowercased). Use Bash:

```bash
grep -iE "^description:.*(<keyword1>|<keyword2>|<keyword3>)" plugins/*/skills/*/SKILL.md skills/*/SKILL.md 2>/dev/null
```

This scans both plugin-resident skills and project-local skills (`skills/*/`, which is where Step 6 saves new skills, so earlier `create-skill` runs are detected). Global skills (`~/.claude/skills/`, plugin cache) are out of scope in this MVP; see `DESIGN.md`.

Each match line shows `path:description-text`. Use the path to identify the skill and the description to judge whether the overlap is genuine.

If any matches look like genuine overlap, surface up to 3 candidates via AskUserQuestion (options):

- "Extend [existing skill name] instead of creating a new one"
- "Create new (the existing skill is different enough)"
- "Cancel and review the existing skill first"

If no matches, say briefly "No overlap with existing skills detected; proceeding." and continue.

If neither `plugins/` nor `skills/` exists or the grep produces no output, skip the check silently.

(This check is intentionally a 1-line grep, not a call to the `list-skills` skill. Reasoning is in `DESIGN.md`. It will migrate to a shared script when `list-skills` exposes one.)

## Step 3: Confirm scoring criteria

Three baseline criteria are always used:

| Criterion | Definition |
|-----------|-----------|
| Conciseness | Every sentence, step, and section earns its place; removing anything would not change the outcome. |
| Runtime efficiency | No anti-patterns from `${CLAUDE_PLUGIN_ROOT}/checklists/runtime-efficiency.md` apply. |
| Simplicity (no overengineering) | No step, loop, sub-agent, or file exists unless its absence would produce a worse outcome. |

Add 1–3 ad-hoc criteria appropriate to this specific skill. Total ≤ 6. Suggestions (pick only what's relevant):

- **Clarity** (for both human readers and Claude as executor): every step is unambiguous; the reader can follow without asking questions.
- **Completeness**: all essential steps and decision points are covered.
- **Safety**: approval points and scope limits are explicit where stakes are non-trivial.
- **Self-reflection quality** (only if the produced skill will include a `## Self-reflection` section): 2–5 MECE criteria appropriate to the generated skill's purpose.
- **Design decision coverage** (only if `DESIGN.md` will hold trade-offs beyond the placeholder row): every intentional trade-off has a row in `DESIGN.md`.

**MECE constraint.** The full selected set (3 baseline + ad-hoc) must be MECE: no two criteria penalise the same flaw. If a proposed criterion overlaps with another, drop the more general one and pick something else.

Present the three baselines plus your suggested ad-hoc additions. Use AskUserQuestion (open text) to confirm or modify, then move on.

## Step 4: Draft the skill

Write a SKILL.md draft with this structure:

```
---
name: [kebab-case-skill-name]
description: [One line: when should this skill activate?]
version: 0.1.0
---

[Body: purpose, steps, decision points, approval gates, scope boundaries]

## Self-reflection
(Include for skills producing durable artifacts. Omit for ephemeral, user-judged output; document omission in DESIGN.md.)

During execution, follow the self-observation protocol (see CLAUDE.md Principles).

[2–5 MECE success criteria go here.]

Follow the self-reflection loop defined in CLAUDE.md (Haiku sub-agent scoring, average ≥ 9.5, max 3 iterations, draft a SKILL.md edit if any criterion stays below 8).
```

Also draft a `DESIGN.md` alongside, with a `# Design decisions` table for any intentional trade-offs. Leave the placeholder row if no decisions exist yet.

Rules specific to this draft (cross-cutting rules live in CLAUDE.md):

- Numbered steps, not paragraphs. Tables for decision logic.
- Include human-approval checkpoints before any action with real-world consequences.
- State what the skill does NOT cover.
- Directory name = kebab-case verb-noun (e.g., `review-invoice`, `onboard-client`). The frontmatter `name` must match the directory exactly: Conductor uses it as the slash-command text, so spaces or capitals break invocation.
- Never write CLI commands, install steps, or configuration syntax you are not certain is correct; flag uncertainty and ask whether to verify or omit.

Show both drafts (SKILL.md + DESIGN.md) to the user. Ask for changes or approval to continue.

## Step 5: Conditional correctness review

Only spawn `feature-dev:code-reviewer` if the draft:

- emits structured data (TSV, JSON) intended for another skill to consume, OR
- contains executable code blocks (bash, python) that will run on the user's machine, OR
- coordinates multiple sub-agent spawns with data passed between them.

Otherwise, skip this step.

If invoked, pass the SKILL.md text, the DESIGN.md text, and this prompt:

> Treat this SKILL.md as executable code. Review net of documented design decisions in the provided DESIGN.md; do not flag intentional trade-offs as bugs. Check:
> (a) Data format fields susceptible to delimiter or newline injection that would corrupt a consuming skill.
> (b) Algorithm edge cases at boundaries: empty list, total items < batch size, deleted item at cursor position.
> (c) Logical contradictions within a single step.
> (d) Implicit formats: any reference to "today", "current date", or "now" without specifying the exact format or shell command (e.g., `date +%Y-%m-%d`).
> (e) Undefined variables used in formulas or conditions.
> (f) Relative paths passed between skills as data; any such path must be absolute.
> (g) Approval gate ordering: irreversible external actions must appear after all automated review steps.
>
> For each issue found, quote the offending text and propose a minimal fix. If no issues are found, say so explicitly.

Apply any fixes to the draft before proceeding. If the `feature-dev:code-reviewer` sub-agent is unavailable, skip this step and note "code-reviewer not available; skipping correctness check."

## Step 6: Confirm and save

Generate the content for all four files now, before asking for approval:

- **SKILL.md**: the draft from Step 4 (post correctness review if Step 5 fired).
- **DESIGN.md**: the draft from Step 4.
- **REQUIREMENTS.md**: assemble from the criteria agreed in Step 3. Format:

   ```
   # Quality requirements

   This skill must satisfy the following, scored 0–10 each, average ≥ 9.5:

   ## Baseline (always)
   - **Conciseness**: every sentence, step, and section earns its place; removing anything would not change the outcome.
   - **Runtime efficiency**: no anti-patterns from `${CLAUDE_PLUGIN_ROOT}/checklists/runtime-efficiency.md` apply.
   - **Simplicity**: no step, loop, sub-agent, or file exists unless its absence would produce a worse outcome.

   ## Ad-hoc (specific to this skill)
   - **[Criterion name]**: [definition]
   ```

   Include only the ad-hoc criteria selected in Step 3. If none, omit the "Ad-hoc" section.

- **HELP.md**: one plain-text paragraph, no heading or frontmatter:

   **`<skill-name>`** <one sentence: what it does and who would use it>. **Example:** "<concrete scenario from the user's Step 1 source>" → `/<skill-name>`.

Show all four file drafts to the user. Use AskUserQuestion (open text) for explicit approval before writing any files.

On approval:

1. Use Bash to create the directory `skills/<skill-name>/`.
2. Use Write to save `skills/<skill-name>/SKILL.md`.
3. Use Write to save `skills/<skill-name>/DESIGN.md`.
4. Use Write to save `skills/<skill-name>/REQUIREMENTS.md`.
5. Use Write to save `skills/<skill-name>/HELP.md`.

## Step 7: Update project documentation

Use Read to check whether `README.md` and `CLAUDE.md` exist at the project root. For each that exists, scan for a skills section: a `## Skills` heading, a Markdown table with a "Skill" column header, or a bullet list of skill names. If neither file contains a skills section, skip this step silently.

For each file that has a skills section, propose adding the new skill using its frontmatter `name` and `description`. Show the exact text to be inserted, matching the surrounding format (table row or bullet line).

Use AskUserQuestion (multiSelect: true, pre-select all candidates):

> "I found a skills list in [file(s)]. Add the new skill there?"

For each confirmed file, use Edit to insert the entry into the existing table or list. Do not create a new section; only append to existing ones.

## Step 8: Hand off to audit-skill (terminal)

This is the final step. Resolve the absolute path first: run `realpath skills/<skill-name>/SKILL.md` via Bash and use that output. Open an `audit-skill` session and pass the absolute path in the opening message.

If `audit-skill` is unavailable, run a minimal inline check:

- Frontmatter parses as valid YAML and contains `name`, `description`, and `version`.
- The `name` value matches the directory name exactly.
- The file contains at least one numbered step.

Report any failures. Tell the user explicitly: "This fallback verifies structural validity only; it does NOT satisfy the REQUIREMENTS.md scoring contract (average ≥ 9.5). Re-run `audit-skill` when available before treating the skill as quality-checked." Do not attempt further iteration: the user can re-run `audit-skill` later or rerun `create-skill` with new feedback.
