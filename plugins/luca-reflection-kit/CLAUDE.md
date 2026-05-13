# luca-reflection-kit

Runtime instructions active whenever this plugin's skills are in use.

## Audience

Same Claude Code users as luca-ops-kit: non-technical staff, managers, and power users inside partner companies. Reflection skills must use plain language and never assume technical fluency.

## Principles

- **Lightweight.** Reflection skills run on demand or hook triggers. Never block user workflows or add mandatory gates.
- **No auto-apply.** Skills may suggest edits to other plugins' skills, memory files, or CLAUDE.md rules. Present all suggestions with exact proposed text. Apply only on explicit user approval.
- **No cross-contamination.** Reflection logs and memory updates belong to the user's machine. Never write to shared or plugin-owned paths.
- **Token efficiency.** Log aggregation runs in Bash before loading into context. Never cat full log files when a summary suffices.
- **Schema resilience.** Skills handle both schema 1 (typed findings objects) and schema 2 (plain strings) reflect log entries. Silently skip unknown schema values.

## Skills

| Skill | Trigger | What it does |
|-------|---------|-------------|
| **reflect** | "reflect", "let's reflect" | Scans the current conversation for errors, workflow patterns, knowledge gaps, and unnecessary questions; presents classified findings; writes chosen learnings to memory or skill files |
| **dream** | "dream", "/dream" | Mines past /reflect session logs to surface recurring patterns, memory contradictions, and improvements that keep coming up but never land |

## Hook

| Hook | Event | What it does |
|------|-------|-------------|
| **optimization-hint** | UserPromptSubmit | Reminds Claude to append a one-sentence optimization hint when the prior response involved 8+ tool calls |
