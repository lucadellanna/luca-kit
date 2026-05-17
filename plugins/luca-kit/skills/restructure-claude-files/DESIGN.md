# Design decisions

Only non-intuitive choices documented here. Defaults and common-sense choices live in `SKILL.md`.

| Decision | Rationale |
|----------|-----------|
| Split out of the original `audit-claude` skill into two commands: `/restructure-claude-files` and `/compact-claude-files` | Restructuring (cross-file moves, scope rebalancing) and compaction (within-file) live at different risk tiers. Bundling them forced every run to clear the higher bar. Splitting lets users compact frequently and restructure deliberately. |
| Sub-agents read the file themselves (`tools: [Read]`) instead of orchestrator passing content via prompt | For any file larger than the Read tool definition (usually true), reading in-agent is cheaper in total tokens and keeps file content out of the orchestrator's main context. |
| Structural reviewer returns both `tighten` and `move` findings; this command uses only `move` and records `tighten` count for the cross-suggestion bridge | One agent, two consumers (compact + restructure). Filtering at the caller is simpler than splitting the agent. |
| Memory move-outs auto-applied only to the co-located memory directory; non-memory targets stay as advice | Memory directories co-located with each CLAUDE.md have unambiguous scope. Non-memory targets (skills, hooks, path rules, templates) require user judgment about the right destination. |
| Cross-reviewer accepts `rule:` prefix in addition to `CLAUDE.md:` and `memory:` | Path-rule files are part of the auto-loaded file set. Including them lets the reviewer find path-rule candidates that already have a home (existing rule file), and detect rule content that should actually be a CLAUDE.md standing rule. |
| Verifier flags only "load-bearing" loss, not any content change | The skill's PURPOSE is to move content out. The verifier exists to catch ACCIDENTAL loss of rule-application info that was not actually moved, not to police every deletion. Bar: would a reader applying the rule make a different decision because of the change? |
| Selective per-item restoration (Keep / Restore / Ambiguous), not all-or-nothing | All-or-nothing rollback undoes good move-outs to fix one false-alarm flag. The orchestrator triages verifier findings inline: false alarms (content was moved to memory) noted, genuine losses restored automatically, ambiguous items surfaced via `AskUserQuestion`. |
| Cross-suggestion is data-driven: only fires when the structural reviewer reported tightenings | Always suggesting the other command would be a nag. Counting the actual findings makes the bridge informative and earns its place at the end of the report. |
