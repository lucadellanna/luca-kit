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

Use Read to attempt to open `~/.claude/memory/work-context.md` (global path, not project-relative). If the file does not exist, Read will return an error; treat that as "no file exists".

**If the file exists:** Read it fully. Extract and hold all current field values in memory (including the `last_updated` date from the YAML frontmatter, and both Company and Role sections with any additional fields). Show the user a brief plain-language summary (company name, role title, last updated date). Then ask using AskUserQuestion (open text):

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

If any fields are blank, batch them into a single follow-up question using AskUserQuestion (open text). Do not ask more than one follow-up question. Example:

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

Ask using AskUserQuestion (open text):

> "Does this look right? Reply with any corrections, or just say yes to save it."

If the user provides corrections, update the block and show it again. Repeat until the user says yes, or until 3 correction rounds have passed. At that point use AskUserQuestion (open text) to ask: "Shall I save this version?" If the user says no, stop without writing any files.

Do not write any file until the user explicitly confirms.

## Step 6: Write

Use Bash to run `mkdir -p ~/.claude/memory` to ensure the directory exists. Then use Write to save the following file at `~/.claude/memory/work-context.md` (global path, outside the project or git repo, survives Conductor workspace rotation), using today's date for the `last_updated` field:

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

Then update `~/.claude/MEMORY.md`. Use Read to check if the file exists and its current content (Read returns an error if the file is missing):
- If the file exists: use Edit to add a line `- [Work Context](memory/work-context.md): company and role background for all tasks` under a `## Context` section (create the section at the end of the file if missing; skip if an entry for `work-context.md` already exists).
- If the file does not exist: use Write to create it with a `## Context` header and that single entry line.

Confirm to the user: "Saved. Claude will now use this context automatically in every future session."

## Self-reflection

During execution, follow the self-observation protocol (see CLAUDE.md Principles).

Spawn a Haiku sub-agent. Pass it:
1. The user's verbatim answers from Steps 2–4
2. The full content of the written `~/.claude/memory/work-context.md`
3. The instruction: "Score each criterion 0–10. For each criterion, give a one-sentence rationale. Return a markdown table, no preamble."

Score the following 5 MECE criteria 0–10:

| Criterion | What to check |
|-----------|---------------|
| Completeness | Every field the user supplied is captured (none dropped); no field is filled in without user input (none hallucinated) |
| Accuracy | Extracted values match verbatim answers: no changed meaning, no hallucinated details |
| Human approval respected | File was not written before user confirmed in Step 5 |
| Index updated | MEMORY.md has a pointer to `work-context.md` |
| Token efficiency | Gap check skipped when all fields present; partial-update routing skipped unselected steps |

If any criterion scores below 8, draft a concise edit to this SKILL.md to prevent the same failure, show it to the user, and use Edit to apply it on approval.

