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

- **Tasks completed** — what was asked for, what was delivered, whether accepted or revised
- **Errors and corrections** — Claude mistakes, user pushback (explicit: "no, I meant..."; implicit: rephrasing, abandoning a line); positive signals too (accepted, praised, built on)
- **Workflow patterns** — repeated sequences, tool chains, procedures done more than twice in a similar way
- **Knowledge gaps** — things Claude got wrong, had to look up, or where the user supplied domain knowledge Claude lacked

## Step 2: Classify Findings

Classify each finding into one action category:

**Write to memory**: Context, preferences, or knowledge that should persist. Examples: "User prefers concise output", "When user says 'post' without qualifier, they mean LinkedIn".

**Create a new skill**: A reusable procedure that doesn't exist yet. Must meet three criteria: (1) would apply more than once, (2) has clear inputs and outputs, (3) is complex enough that instructions help.

**Improve an existing skill**: A skill produced suboptimal results, missed an edge case, or could be extended. Reference the specific skill and the specific change.

**No action needed**: Worth noting as an insight but doesn't warrant a persistent change.

## Step 3: Score and Revise

Spawn a Haiku sub-agent to score the current findings. Pass it:
1. The full findings list
2. These criteria and their definitions
3. The instruction: "Score each criterion 0–10. For each, give a one-sentence rationale. Return a markdown table."

Criteria:
1. **Precision** — each finding is scoped correctly: not too broad ("Claude made mistakes") nor too narrow (a single-message detail that doesn't generalise)
2. **Non-triviality** — no generic observations that apply to any conversation
3. **Concreteness** — every actionable finding names a specific next step that can be executed immediately
4. **Coverage** — no obvious patterns or errors from the conversation were missed
5. **Accuracy** — each finding is factually grounded: the events, errors, and patterns described actually occurred as stated in the conversation

Use the sub-agent's scores directly. If average < 9.5, revise the findings and re-score. Stop after 3 iterations or if the score stops improving. Note: if the score remains stagnant or increases by < 0.5, you may continue for one more iteration if the previous changes were substantive, as this may be Haiku scoring variance rather than a lack of progress. Do not present findings until the threshold is met or iterations are exhausted.

## Step 4: Present Findings

Present grouped by action category. Omit empty categories. Mark each item **High** or **Medium** priority.

- **Insights**: Findings worth noting, 1-2 sentences each.
- **Suggested Memory Updates**: What to remember and why.
- **Skill Opportunities**: Proposed name, purpose, trigger, why it's worth creating.
- **Skill Improvements**: Which skill, what's wrong, the specific change.

Ask the user what to implement via AskUserQuestion (multiSelect: true) with the specific items as options.

## Step 5: Act on Choices

**Memory updates**: State the exact text to be added (one or two lines), then write it to `.claude/memory/MEMORY.md` under `## Preferences` or `## Context` (create file/section if needed). Terse entries only — just what Claude needs to know.

**New skills**: Run `/create-skill` with the proposed name, purpose, and trigger as context.

**Skill improvements**: State the planned edit (one line), then apply it. One focused edit per finding.

## Self-reflection

After acting on choices, spawn a Haiku sub-agent to verify:

1. **Impact** — if any actions were selected: at least one was successfully applied. Auto-pass if the user declined all proposed actions or only insights were surfaced.
2. **Quality** — findings passed the Step 3 gate: average ≥ 9.5 was achieved, OR all 3 iterations were completed. Reaching max iterations is a passing condition, not a failure.
3. **No overreach** — no actions were taken beyond what the user selected

If any criterion scores below 8, draft a concise edit to this SKILL.md to prevent the same failure, show it to the user, and apply on approval.

## Design decisions

| Decision | Rationale |
|----------|-----------|
| Haiku sub-agent for findings scoring (Step 3) | CLAUDE.md-mandated pattern — reduces confirmation bias and is cheaper than inline scoring; apparent token overhead is intentional |
