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
| **audit-claude** | "/audit-claude", "audit my CLAUDE.md" | Tightens your CLAUDE.md and memory files by removing redundancy, surfacing cross-type mismatches (CLAUDE.md vs memory, path-rule candidates), and flagging scope mismatches between project and global |

## Agents

| Agent | Used by | Mandate |
|---|---|---|
| **claude-md-structural-reviewer** | audit-claude | Returns within-file tightenings and move-out recommendations for content that belongs in memory, path rules, skills, or hooks (Sonnet, `tools: [Read]`) |
| **claude-md-compression-reviewer** | audit-claude | Returns sentence-level micro-compressions (Haiku, `tools: [Read]`) |
| **claude-md-loss-verifier** | audit-claude | Reads pre- and post-edit versions and reports any meaningful content lost (Haiku, `tools: [Read]`) |
| **claude-md-scope-reviewer** | audit-claude | Reads both project and global CLAUDE.md, returns promote/demote/duplicate recommendations for scope mismatches (Sonnet, `tools: [Read]`) |
| **claude-md-cross-reviewer** | audit-claude | Reads all discovered CLAUDE.md and memory files, returns memory-to-CLAUDE.md candidates and path-rule suggestions (Sonnet, `tools: [Read]`) |
