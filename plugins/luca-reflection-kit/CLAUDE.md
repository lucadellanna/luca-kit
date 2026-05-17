# luca-reflection-kit

Runtime instructions active whenever this plugin's skills are in use.

## Audience

Same Claude Code users as luca-ops-kit: non-technical staff, managers, and power users inside partner companies. Reflection skills must use plain language and never assume technical fluency.

## Principles

- **Lightweight.** Reflection skills run on demand or hook triggers. Never block user workflows or add mandatory gates.
- **Auto-apply only on safe targets.** Skills may suggest edits to memory files, CLAUDE.md rules, skill files, and hook scripts. Risk is derived from the target file: project or global `MEMORY.md` is `safe` (auto-apply after a literal duplicate check); any `CLAUDE.md`, skill file, or new skill is `ambiguous` (ask); hook scripts are `security-sensitive` (ask). Anything else defaults to `breaking` (ask).
- **No cross-contamination.** Reflection logs and memory updates belong to the user's machine. Never write to shared or plugin-owned paths.
- **Token efficiency.** Log aggregation runs in Bash before loading into context. Never cat full log files when a summary suffices.
- **Schema resilience.** Skills handle schemas 1 (typed findings objects), 2 (plain strings), and 3 (structured applied / asked_accepted / asked_rejected / hints) reflect log entries. Normalization happens at the load layer (`scripts/migrate-log.py`); the rest of the skill sees one shape. Unknown schemas are silently skipped.
- **Local-only acknowledgment, schema-locked.** The terms marker lives under `~/.claude/luca-kit/`. No server calls. Schema is locked at `{"version": "1.0", "accepted_at": "<ISO 8601>"}`; schema changes require a version bump in the filename (`v1` to `v2`).

## Skills

| Skill | Trigger | What it does |
|-------|---------|-------------|
| **reflect** | "reflect", "let's reflect" | Orchestrates two specialist reviewers (Claude-side and user-side) over a verbatim conversation digest; surfaces findings with verbatim evidence; auto-applies gated memory entries; asks before any other change |
| **dream** | "dream", "/dream" | Mines past /reflect session logs to surface recurring patterns, memory contradictions, and improvements that keep coming up but never land |
| **setup-context-search** | "/setup-context-search", "set up context search", "install qmd" | One-time wizard: installs qmd and configures it as an MCP server; enables semantic overlap detection in /reflect and /dream |

## Commands

| Command | What it does |
|---|---|
| **/luca-reflection-kit:accept-terms** | Prints the interim notice, asks the user via AskUserQuestion, writes `~/.claude/luca-kit/terms-accepted-v1.json` on acknowledgment with `{"version": "1.0", "accepted_at": "<ISO 8601>"}`. On "Not right now", removes the marker if it exists. Always re-prompts; re-run = re-decide. |
| **/luca-reflection-kit:luca-reflection-recommended-setup** | Asks once whether to save private session notes after each /reflect. Writes `~/.claude/reflect-logs/.enabled` or `.disabled`. Re-running always re-prompts. |

## Agents

| Agent | Used by | Mandate |
|-------|---------|---------|
| **claude-flow-reviewer** | reflect | Reviews a conversation digest for Claude-side improvements: missed skill invocations, weak rule triggers, skill/rule/memory edits, repeated failure patterns |
| **user-flow-reviewer** | reflect | Surfaces up to 3 user-facing recommendations as Hints. Plain language, no coaching, nothing written to disk. |

## Hooks

| Hook | Event | What it does |
|------|-------|-------------|
| **optimization-hint** | UserPromptSubmit | Reminds Claude to append a one-sentence Optimization hint at the end of the current response if it involves 8+ tool calls (memory-worthy pattern / skill to edit or improve) |
| **workflow-hint** | UserPromptSubmit | Reminds Claude to append a one-sentence Workflow hint at the end of the current response if it involves 8+ tool calls (skill to codify / user judgement or workflow to automate / friction to remove) |
| **terms-acceptance-check** | SessionStart | Echoes a one-time reminder if `~/.claude/luca-kit/terms-accepted-v1.json` is absent. Silent when `$CLAUDE_CODE_REMOTE` is set or no controlling terminal exists; silent once the marker exists. |
| **consolidate-reflect-queue** | PreToolUse (Skill) | Before any claude-reflect skill runs in a Conductor workspace, merges learnings-queue.json from all sibling workspace project folders into the current workspace's queue and clears the siblings. No-op outside Conductor workspaces. |
