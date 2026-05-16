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
| `audit-claude` | "/audit-claude", "audit my CLAUDE.md" | Tightens your project and global CLAUDE.md files by removing redundancy, content that belongs elsewhere, and scope mismatches |
