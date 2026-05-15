# luca-kit

Runtime instructions active whenever this plugin's skills are in use.

## Audience

Claude Code users of any technical level. Skills and hooks must use plain language and never assume deep technical fluency.

## Principles

- **Lightweight.** Features run on demand or hook triggers. Never block user workflows or add mandatory gates.
- **No cross-contamination.** Memory updates belong to the user's machine. Never write to shared or plugin-owned paths.
- **Token efficiency.** Use Bash aggregation instead of loading full files into context when a summary suffices.

## Hooks

| Hook | Event | What it does |
|---|---|---|
| **optimization-hint** | UserPromptSubmit | Reminds Claude to append a one-sentence Optimization hint at the end of the current response if it involves 8+ tool calls (memory-worthy pattern / skill to edit or improve) |
| **workflow-hint** | UserPromptSubmit | Reminds Claude to append a one-sentence Workflow hint at the end of the current response if it involves 8+ tool calls (skill to codify / user judgement or workflow to automate / friction to remove) |

## Skills

| Skill | Trigger | What it does |
|---|---|---|
| **reflect** | "reflect", "let's reflect", "/reflect" | Highlights what to improve in how you and Claude work together, so the next conversation goes better |
