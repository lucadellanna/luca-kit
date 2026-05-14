# luca-reflection-kit

Runtime instructions active whenever this plugin's skills are in use.

## Audience

Same Claude Code users as luca-ops-kit: non-technical staff, managers, and power users inside partner companies. Reflection skills must use plain language and never assume technical fluency.

## Principles

- **Lightweight.** Reflection skills run on demand or hook triggers. Never block user workflows or add mandatory gates.
- **Auto-apply only behind a strict gate.** Skills may suggest edits to other plugins' skills, memory files, or CLAUDE.md rules. Default behavior is to present suggestions with exact proposed text and apply only on explicit user approval. Auto-apply without approval is allowed only when ALL of: target is `.claude/memory/MEMORY.md`, confidence is high, proposed text is ≤2 lines, and the text is not a duplicate of an existing line in MEMORY.md or CLAUDE.md. Anything failing any criterion must ask.
- **No cross-contamination.** Reflection logs and memory updates belong to the user's machine. Never write to shared or plugin-owned paths.
- **Token efficiency.** Log aggregation runs in Bash before loading into context. Never cat full log files when a summary suffices.
- **Schema resilience.** Skills handle both schema 1 (typed findings objects) and schema 2 (plain strings) reflect log entries. Silently skip unknown schema values.
- **Local-only acknowledgment, schema-locked.** The terms marker lives under `~/.claude/luca-ops-kit/`. No server calls. Schema is locked at `{"version": "1.0", "accepted_at": "<ISO 8601>"}`; schema changes require a version bump in the filename (`v1` to `v2`).

## Skills

| Skill | Trigger | What it does |
|-------|---------|-------------|
| **reflect** | "reflect", "let's reflect" | Orchestrates two specialist reviewers (Claude-side and user-side) over a verbatim conversation digest; surfaces findings with verbatim evidence; auto-applies gated memory entries; asks before any other change |
| **dream** | "dream", "/dream" | Mines past /reflect session logs to surface recurring patterns, memory contradictions, and improvements that keep coming up but never land |

## Commands

| Command | What it does |
|---|---|
| **/luca-reflection-kit:accept-terms** | Prints the interim notice, asks the user via AskUserQuestion, writes `~/.claude/luca-ops-kit/terms-accepted-v1.json` on acknowledgment with `{"version": "1.0", "accepted_at": "<ISO 8601>"}`. On "Not right now", removes the marker if it exists. Always re-prompts; re-run = re-decide. |
| **/luca-reflection-kit:luca-reflection-recommended-setup** | Asks once whether to save private session notes after each /reflect. Writes `~/.claude/reflect-logs/.enabled` or `.disabled`. Re-running always re-prompts. |

## Agents

| Agent | Used by | Mandate |
|-------|---------|---------|
| **claude-flow-reviewer** | reflect | Reviews a conversation digest for Claude-side improvements: missed skill invocations, weak rule triggers, skill/rule/memory edits, repeated failure patterns |
| **user-flow-reviewer** | reflect | Surfaces recommendations and classifies each as automatable (becomes a Claude-side rule, routed to the claude-flow pipeline) or user-only (rendered as a Hint to the user, max 3). Plain language, no coaching |

## Hooks

| Hook | Event | What it does |
|------|-------|-------------|
| **optimization-hint** | UserPromptSubmit | Reminds Claude to append a one-sentence optimization hint when the prior response involved 8+ tool calls |
| **terms-acceptance-check** | SessionStart | Echoes a one-time reminder if `~/.claude/luca-ops-kit/terms-accepted-v1.json` is absent. Silent when `$CLAUDE_CODE_REMOTE` is set or no controlling terminal exists; silent once the marker exists. |
