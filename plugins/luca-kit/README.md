# luca-kit

Self-reflection and productivity hooks for Claude Code.

## Hooks

| Hook | Event | Effect |
|---|---|---|
| `optimization-hint` | UserPromptSubmit | After responses with 8+ tool calls, reminds Claude to surface a one-sentence memory-worthy pattern or skill improvement |
| `workflow-hint` | UserPromptSubmit | After responses with 8+ tool calls, reminds Claude to surface a one-sentence automation or friction-removal hint |

## Skills

| Skill | Trigger | Effect |
|---|---|---|
| `reflect` | "reflect", "let's reflect", "/reflect" | Highlights what to improve in how you and Claude work together, so the next conversation goes better |
| `compact-claude-files` | "/compact-claude-files", "compact my CLAUDE.md" | Shortens your CLAUDE.md, memory, and path-rule files by applying within-file tightenings and compressions |
| `restructure-claude-files` | "/restructure-claude-files", "restructure my CLAUDE.md" | Moves content out of CLAUDE.md to memory, surfaces cross-type transfer candidates, and flags scope mismatches between project and global |
| `list-skills` | "what skills do I have?", "list skills", "show available workflows" | Shows every installed skill across all plugins with its description and line count in a single table |
