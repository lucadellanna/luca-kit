# luca-reflection-kit

Self-reflection and cross-session learning skills for Claude Code and Claude Cowork. Scan conversations for improvement points, mine recurring patterns across sessions, and get a token-efficient optimization hint after high-tool-count turns.

## Installation

### Claude Code

Requires [Claude Code](https://claude.ai/code).

1. `/plugin marketplace add lucadellanna/luca-kit`
2. `/plugin install luca-reflection-kit@lucadellanna`
3. Enable auto-updates: type `/plugin`, press Tab twice to open the Marketplaces tab, select `luca-reflection-kit`, and select **Enable updates**.
4. Run `/luca-reflection-kit:luca-reflection-recommended-setup` to configure session notes and privacy settings.

### Claude Cowork

1. Left sidebar → Customize → Plugins → Personal → **+** → Add marketplace → `lucadellanna/luca-kit`
2. You will see all available luca-kit plugins; click **+** next to each one you want to install
3. Enable auto-updates: Browse Plugins → Personal → luca-reflection-kit → **···** → Sync automatically
4. Run `/luca-reflection-kit:luca-reflection-recommended-setup` to configure session notes and privacy settings.

**To uninstall:**

```
/plugin uninstall luca-reflection-kit@lucadellanna/luca-kit
```

## Skills

| Skill | What it does |
|-------|-------------|
| **reflect** | After a session, two specialist reviewers surface insights with verbatim evidence: claude-side proposes concrete edits (clear low-risk memory entries are written automatically, everything else asks for your selection); user-side surfaces actionable recommendations for you (skills worth invoking next time, scoping techniques, workflow timing) |
| **dream** | Mines your /reflect session logs to surface patterns across sessions: recurring issues never fixed, memory contradictions, and improvements that keep coming up but never land |

## Agents

Spawned by skills in this plugin (you do not invoke them directly):

| Agent | Used by | Mandate |
|-------|---------|---------|
| **claude-flow-reviewer** | reflect | Reviews a conversation digest for Claude-side improvements: missed skill invocations, weak rule triggers, skill/rule/memory edits worth proposing |
| **user-flow-reviewer** | reflect | Surfaces up to 3 user-facing recommendations as Hints. Plain language, no coaching, nothing written to disk. |

## Hooks

Installed automatically with the plugin (no setup needed):

| Hook | Event | What it does |
|------|-------|-------------|
| **optimization-hint** | UserPromptSubmit | On every prompt, reminds Claude to append a one-sentence optimization hint if the prior response involved 8+ tool calls (reusable skill, memory-worthy pattern, or workflow improvement) |
| **terms-acceptance-check** | SessionStart | Reminds the user (via Claude) to run `/luca-reflection-kit:accept-terms` if no acknowledgment is recorded yet. Silent once acknowledged, and silent in non-interactive sessions (`claude -p`, agent SDK, CI). |

## Commands

| Command | What it does |
|---|---|
| **/luca-reflection-kit:accept-terms** | Shows the interim notice for Luca's plugins and records your decision locally. One-time per Claude install. No server calls. |
| **/luca-reflection-kit:luca-reflection-recommended-setup** | Configure session notes for /reflect. Decides once whether to save private logs to your computer. |

## License

Source-available, not open-source. You may inspect the repository and use it for personal evaluation. Commercial, client-facing, team, or organizational use requires a paid license. Contact [Luca@Luca-Dellanna.com](mailto:Luca@Luca-Dellanna.com) for more information.
