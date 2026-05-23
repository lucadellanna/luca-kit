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
| **compact-claude-files** | "/compact-claude-files", "compact my CLAUDE.md" | Tightens your CLAUDE.md, memory, and path-rule files by applying within-file tightenings and sentence-level compressions |
| **restructure-claude-files** | "/restructure-claude-files", "restructure my CLAUDE.md" | Moves content out of CLAUDE.md to memory, surfaces memory-to-CLAUDE.md and path-rule candidates, and flags scope mismatches between project and global |
| **list-skills** | "what skills do I have?", "list skills", "show available workflows" | Shows every installed skill across all plugins with its description and line count in a single table |

## Agents

| Agent | Used by | Mandate |
|---|---|---|
| **claude-md-structural-reviewer** | compact-claude-files (tightenings), restructure-claude-files (move-outs) | Returns within-file tightenings and move-out recommendations for content that belongs in memory, path rules, skills, or hooks (Sonnet, `tools: [Read]`) |
| **claude-md-compression-reviewer** | compact-claude-files | Returns sentence-level micro-compressions on CLAUDE.md, memory, and path-rule files (Haiku, `tools: [Read]`) |
| **claude-md-loss-verifier** | compact-claude-files, restructure-claude-files | Reads pre- and post-edit versions and reports any meaningful content lost (Haiku, `tools: [Read]`) |
| **claude-md-scope-reviewer** | restructure-claude-files | Reads both project and global CLAUDE.md, returns promote/demote/duplicate recommendations for scope mismatches (Sonnet, `tools: [Read]`) |
| **claude-md-cross-reviewer** | restructure-claude-files | Reads all discovered CLAUDE.md, memory, and path-rule files, returns memory-to-CLAUDE.md candidates and path-rule suggestions (Sonnet, `tools: [Read]`) |
