---
name: reflect
description: >
  Use this skill when the user says "reflect", "let's reflect", "/reflect",
  or asks what could be improved about how the current conversation has
  gone. Surfaces a few concrete improvements to how the user and Claude
  work together, so the next conversation goes better.
version: 0.1.0
---

# Reflect

Read the conversation since the last reflect trigger in this session, or from the start if this is the first one. Scan backward for the most recent user message that triggered this skill; start after that turn. Look for improvements using the table below.

**In scope:** the conversation flow itself, i.e. how the user and Claude interacted, what tripped up the work, what the user had to repeat or correct.

**Out of scope:** auditing the quality of any artifact produced during the conversation (missing files, frontmatter quality, naming collisions, code style). That is a code review, which is a different workflow.

## What to look for

### Claude-side (how Claude worked)

| Observation | Suggest |
|---|---|
| A tool, API, read, or write error with a likely-recurring root cause | A fix that prevents the whole class of error, not just this instance |
| Something took a long time to figure out and you expect to do it again | A new skill, or a memory entry |
| User feedback on Claude's work that generalises beyond this task | A CLAUDE.md principle, a path rule, a memory entry, or a skill, whichever fits |
| Claude asked the user a question it could have answered itself | Edit the relevant skill, memory, or note so Claude does not need to ask again |

### User-side (how the user worked with Claude)

| Observation | Suggest |
|---|---|
| The user had to correct Claude because their initial instructions left out context Claude needed | Coach the user on what to include next time |
| The user reversed a recent decision without explaining why | Ask once what shifted, so the new direction can be remembered as a preference |
| The user repeatedly asked the same kind of follow-up | Suggest a default that the user could set so the follow-up becomes implicit |
| The user's instructions conflicted with an earlier stated rule or preference | Surface the conflict and ask which one wins going forward |

## How to suggest

- **Internally cap at three per side.**
- **Do not invent findings to balance the two sides.** No comment needed about the absence.
- **Only suggestions that would save time next time.** Not nitpicks about situations unlikely to repeat.
- **Do not re-suggest** anything you already proposed earlier in this session.
- **For Claude-side suggestions, pick the right home** in this order of preference:
  1. **Path rule** if it is a constraint on a specific path or filetype.
  2. **Skill** if it is a repeatable procedure with clear triggers. Keep the skill as concise as possible.
  3. **CLAUDE.md principle** only if you expect it to apply often across tasks. One-offs go in memory instead.
  4. **Memory entry** for everything else worth remembering.
- **For user-side suggestions, the fix is coaching, not a file edit.** Phrase it as a concrete habit the user can adopt next time.

## How to present

Use the two tables above only as an internal checklist when looking for observations. Present findings in two bullet point lists:

**Changes to apply** (code, config, skills, memory, or CLAUDE.md edits Claude will make):
- Each bullet describes the change and why it helps.

**Learning points** (habits or approaches for the user to adopt next time):
- Each bullet describes what to do differently and why it matters.

Plain language in both lists:
- Avoid jargon and internal terms. If a technical word is unavoidable, explain it in the same sentence.
- Describe what was observed in everyday words. Say what would change next time, and why it matters, before naming any rule or file.
- Each bullet stands on its own. The user should be able to read it once and decide.

Omit a list entirely if there are no findings for that side. Do not invent findings to balance the two lists.

**Closing question (conditional):**
- If there are "Changes to apply": end with "Which changes should I implement?"
- If there are only "Learning points": end with "Does any of this resonate, or would you push back on anything?"
- If there are no findings at all: say so briefly and stop.

## After the user replies

- If the user accepts changes, apply them and stop.
- If the user skips any change, ask once why they skipped it. The goal is to learn, not to relitigate.
- If their answer reveals a generalisable preference (not just "not now"), write a memory entry immediately capturing that preference, so future `/reflect` calls do not raise the same kind of suggestion again.
