---
name: Build Work Context
description: Collect and save a durable company-and-role context file so Claude has the background it needs for every future task, without asking the same questions every session.
version: 0.1.0
---

# Build Work Context

You help the user capture a short, durable record of their company and their role. Once saved, Claude will use this automatically on every task; no more re-explaining who you are or what your company does.

This is a meta-skill: it helps users build and maintain their own durable work context. It does not encode a domain procedure.

This skill uses Haiku for information gathering and scoring.

## Step 1: Welcome and check for existing context

Use Read to attempt to open `~/.claude/memory/work-context.md` (global path, not project-relative). If the file does not exist, Read will return an error — treat that as "no file exists".

**If the file exists:** Read it fully. Extract and hold all current field values in memory (including the `last_updated` date from the YAML frontmatter, and both Company and Role sections with any additional fields). Show the user a brief plain-language summary (company name, role title, last updated date). Then ask:

> "I found your existing work context, last updated on [DATE]. Which part would you like to update: your company info, your role info, or both? (Say 'keep' to leave everything as is.)"

- If the user says **company**: run Step 2 only, skip Step 3. **Carry forward all existing Role fields as-is.** Do not treat them as blank.
- If the user says **role**: run Step 3 only, skip Step 2. **Carry forward all existing Company fields as-is.** Do not treat them as blank.
- If the user says **both**: run Steps 2 and 3. No carry-forward needed.
- If the user says **keep**: stop here. No changes needed.

**If no file exists:** Tell the user:

> "This will take about 2 minutes. Once saved, Claude will know your company and your role, so it can give you better, more targeted help from the very first message in any session. If you can, try dictating your answers out loud rather than typing: it's faster and usually gives richer detail."

Then continue to Step 2.

## Step 2: Company interview

Ask the user (AskUserQuestion, open text):

> "Describe your company in 3–4 sentences: what it does, who it serves, and roughly how big it is."

Extract the following fields from their answer:
- **Name**: the company's name
- **What it does**: 1–2 sentence description
- **Industry**: sector or field
- **Size**: approximate headcount (use a band: 1–10, 11–50, 51–200, 201–1000, 1000+)
- **Customers**: who the company serves (e.g., B2B, mid-market retailers; or B2C, working parents)

Also extract any other notable differentiators not covered above (e.g., location, languages, certifications, notable expertise) and include them as additional fields.

If the answer is thin, disorganised, or voice-transcribed (filler words, run-on sentences), extract the best available values. Do not hallucinate details the user did not provide; leave the field blank and flag it for Step 4.

## Step 3: Role interview

Ask the user (AskUserQuestion, open text):

> "Describe your role: your name, your title, what you're mainly responsible for (including what you can decide independently), and what kinds of tasks you want Claude to help you with."

Extract the following fields:
- **Name**: the user's personal name
- **Title**: their job title
- **Responsibilities**: 2–3 key ownership areas
- **Decision authority**: what they can decide independently vs. what requires sign-off
- **Claude use cases**: the tasks they most want Claude to help with

Same extraction rules as Step 2, including the catch-all for notable differentiators not covered by the standard fields.

## Step 4: Gap check (conditional)

Collect every field that is still blank **in the sections that were just updated** (Steps 2 and/or 3). Do not include carried-forward fields from skipped sections; those are already populated from the existing file.

If any fields are blank, batch them into a single follow-up question. Do not ask more than one follow-up question. Example:

> "Just a couple of things I couldn't catch from your answers: [list the missing fields as plain questions, e.g., 'What decisions can you make independently at work?' or 'Roughly how many people work at your company?']"

If no fields are blank, skip this step entirely.

## Step 5: Preview and confirm

Show the user the structured context as a formatted markdown block:

```
Company
  Name: …
  What it does: …
  Industry: …
  Size: …
  Customers: …
  [Additional fields, if any]

Role
  Name: …
  Title: …
  Responsibilities: …
  Decision authority: …
  Claude use cases: …
  [Additional fields, if any]
```

Ask:

> "Does this look right? Reply with any corrections, or just say yes to save it."

If the user provides corrections, update the block and show it again. Repeat until the user says yes, or until 3 correction rounds have passed. At that point ask: "Shall I save this version?" If the user says no, stop without writing any files.

Do not write any file until the user explicitly confirms.

## Step 6: Write

Write the following file at `~/.claude/memory/work-context.md` (global path, outside the project or git repo, survives Conductor workspace rotation), using today's date for the `last_updated` field:

```markdown
---
last_updated: YYYY-MM-DD
---
# Company & Role Context

## Company
**Name:** …
**What it does:** …
**Industry:** …
**Size:** …
**Customers:** …
[Append any additional Company fields here as **Field Name:** Value]

## Role
**Name:** …
**Title:** …
**Responsibilities:** …
**Decision authority:** …
**Claude use cases:** …
[Append any additional Role fields here as **Field Name:** Value]
```

Any additional Company fields go at the end of the `## Company` section; any additional Role fields go at the end of `## Role`. Use `**Field Name:** Value` format, consistent with the standard fields.

Then update `~/.claude/MEMORY.md`:
- If the file exists: add a line `- [Work Context](memory/work-context.md): company and role background for all tasks` under a `## Context` section (create the section at the end of the file if missing; skip if an entry for `work-context.md` already exists).
- If the file does not exist: create it with a `## Context` header and that single entry line.

Confirm to the user: "Saved. Claude will now use this context automatically in every future session."

## Self-reflection

Spawn a Haiku sub-agent. Pass it:
1. The user's verbatim answers from Steps 2–4
2. The full content of the written `~/.claude/memory/work-context.md`

Score the following 5 MECE criteria 0–10:

| Criterion | What to check |
|-----------|---------------|
| Completeness | Every field the user supplied is captured (none dropped); no field is filled in without user input (none hallucinated) |
| Accuracy | Extracted values match verbatim answers: no changed meaning, no hallucinated details |
| Human approval respected | File was not written before user confirmed in Step 5 |
| Index updated | MEMORY.md has a pointer to `work-context.md` |
| Token efficiency | Gap check skipped when all fields present; partial-update routing skipped unselected steps |

If average < 9.5, revise and re-score (max 3 iterations; stop if score does not improve). If any criterion remains below 8 after iteration, draft a concise edit to this SKILL.md to prevent the same failure, show it to the user, and apply on approval.

## Design decisions

| Decision | Rationale |
|----------|-----------|
| Open-ended Q&A instead of field-by-field form | Non-technical users find structured forms intimidating; free text with extraction is more natural and captures nuance |
| Two interview questions before preview | Minimises friction; one gap-fill follow-up is enough if answers are thin; don't turn it into an interview |
| Step 3 explicitly asks for the user's name | Name is rarely volunteered in a professional context without prompting |
| Decision authority hinted in Step 3, gap check as safety net | Step 3 includes "what you can decide independently" to elicit authority naturally; gap check catches it if the user still omits it |
| Gap check covers all blank fields, not just decision authority | Hard-coding one field as the sole trigger would silently drop other missing fields |
| Partial update routing (company / role / both) | Binary update-or-keep forces a full re-run even when only a title changed; routing by section reduces friction for real-world partial updates. Skipped sections are carried forward from the existing file, never treated as blank, to prevent overwriting unchanged data or re-asking answered questions |
| Preview loop capped at 3 rounds | Prevents infinite correction loops; after 3 rounds, ask for explicit save confirmation |
| Voice-style answer handling | Voice input produces filler words and run-on sentences; extractor must handle gracefully, flagging blanks rather than hallucinating |
| File at `~/.claude/memory/work-context.md` | Global path: never in git, survives Conductor workspace rotation, available in every project and future workspace |
| Index pointer in `~/.claude/MEMORY.md` | Global MEMORY.md is loaded in all projects and all Conductor instances; the only index that satisfies the cross-workspace availability requirement |
| `last_updated` date in frontmatter | Context goes stale; the date makes staleness visible without opening the file |
| Do not collect: projects, KPIs, tech stack, team roster, competitive info | Too volatile or too sensitive; belongs in project-level context, not a persistent work profile |
| `last_updated` uses date from session context, not a system call | Claude Code provides `currentDate` in every session via system prompt; no tool call needed. The `YYYY-MM-DD` placeholder in the template is replaced at runtime with that value. |
| MEMORY.md update logic handles three cases explicitly | File exists with section, file exists without section, file doesn't exist. Three cases are necessary; simplifying to "append" would create duplicate entries on re-runs. |
| Self-modification in Self-reflection is intentional | Drafting a skill edit on scoring failure is the standard luca-ops-kit quality loop, applied in all skills. Changes require user approval before writing; no silent self-modification occurs. |
