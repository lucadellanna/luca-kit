---
name: reflect
description: >
  Use this skill when the user says "reflect", "let's reflect", or asks to
  analyze the current conversation for learning points, errors, and improvement
  opportunities. Scans tasks, errors, user feedback, and workflow patterns to
  extract actionable insights. Can write learnings to memory and propose
  improvements to the plugin's own skills.
version: 0.1.0
---

# Reflect

Analyze the current conversation to extract learning points, catch errors, and detect opportunities for skill creation or improvement. Present findings and act on what the user chooses.

## Step 1: Scan and Extract

**CRITICAL**: Do not restate what happened in the conversation. The goal is to extract learnings and improvements, not to summarize the task.

If the conversation has fewer than ~5 substantive exchanges, say "Not enough material to reflect on meaningfully" and stop.

Otherwise, review the full conversation. For each noteworthy item, capture: what happened (one sentence), why it matters, and a specific actionable takeaway. Discard trivial items.

Scan these four areas:

**Tasks completed**: What was asked for, what was delivered, whether the result was accepted or revised.

**Errors and corrections**: Where Claude made mistakes or the user pushed back. Include explicit corrections ("no, I meant...") and implicit ones (user rephrasing, abandoning a line, asking for a different approach). Note positive feedback signals too (user accepted, praised, built on the output).

**Workflow patterns**: Repeated action sequences, multi-step procedures that worked well, tool chains that produced good results. Anything done more than twice in a similar way.

**Knowledge gaps**: Things Claude had to look up, got wrong, or where the user supplied domain knowledge Claude lacked.

## Step 2: Classify Findings

Classify each finding into one action category:

**Write to memory**: Context, preferences, or knowledge that should persist. Examples: "User prefers concise output", "When user says 'post' without qualifier, they mean LinkedIn".

**Create a new skill**: A reusable procedure that doesn't exist yet. Must meet three criteria: (1) would apply more than once, (2) has clear inputs and outputs, (3) is complex enough that instructions help.

**Improve an existing skill**: A skill produced suboptimal results, missed an edge case, or could be extended. Reference the specific skill and the specific change.

**No action needed**: Worth noting as an insight but doesn't warrant a persistent change.

## Step 3: Score and Revise

Score the current set of findings on each criterion (0–10):

1. **Specificity** — each finding names exactly what happened, not a vague pattern
2. **Non-triviality** — no generic observations that apply to any conversation
3. **Actionability** — every actionable finding has a concrete next step, not just an observation
4. **Coverage** — no obvious patterns or errors from the conversation were missed

If average < 9.5, revise the findings and re-score. Stop after 3 iterations or if the score stops improving. Do not present findings until the threshold is met or iterations are exhausted.

## Step 4: Present Findings

Present grouped by action category. Omit empty categories.

- **Insights**: Findings worth noting, 1-2 sentences each.
- **Suggested Memory Updates**: What to remember and why.
- **Skill Opportunities**: Proposed name, purpose, trigger, why it's worth creating.
- **Skill Improvements**: Which skill, what's wrong, the specific change.

Then ask the user what to implement via AskUserQuestion (multiSelect: true) with the specific items as options.

## Step 5: Act on Choices

**Memory updates**: Add to `.context/MEMORY.md` under `## Preferences` or `## Context`. Create the file if it does not exist. Create the section if it does not exist. Keep entries terse — just what Claude needs to know, no narrative. Do not write memory updates into versioned docs like `CLAUDE.md`.

**New skills**: Run `/create-skill` to build the skill interactively. Pass the proposed name, purpose, and trigger as context so the guided flow starts with those already decided.

**Skill improvements**: Read `skills/<name>/SKILL.md`, apply the change directly. One focused edit per finding.

## What NOT to Do

- Don't restate what the user asked for or what was delivered — that's summarizing, not reflecting
- Don't manufacture insights from trivial exchanges or short conversations
- Don't minimize real errors or overclaim successes
- Don't propose skills for one-off tasks
- Don't write narrative memory entries — keep them terse, just what Claude needs to know
