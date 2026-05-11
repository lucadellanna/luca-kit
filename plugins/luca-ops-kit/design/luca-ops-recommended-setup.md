# Design decisions

| Decision | Rationale |
|----------|-----------|
| Marker at `~/.claude/luca-ops-kit/setup-complete` (not a root dotfile) | Plugin-namespaced path avoids polluting `~/.claude/` root; survives backup/restore cycles without false triggers |
| Fingerprint comments in CLAUDE.md rules | Enables precise removal by `undo-setup` without content-matching; invisible during normal reading; survives user edits to surrounding text |
| Fingerprints are the source of truth (no manifest) | Rules are self-identifying via their fingerprint comment; `undo-setup` greps for fingerprints directly instead of reading a manifest. Eliminates manifest write/merge/lock machinery. Possible because the only artifacts are tagged lines in a single file. |
| Hooks moved to plugin-level hooks.json (v0.3.0) | The optimization-hint hook has no security or privacy sensitivity (a one-line echo). Plugin-level hooks auto-install and auto-uninstall with the plugin, eliminating user-facing setup/teardown steps, manifest tracking, settings.json writes, lock files, backup/restore logic, and code-reviewer gates. |
| No `applied.json` manifest | With hooks at the plugin level and rules identified by fingerprint, the manifest has no remaining purpose. Detection (grep for fingerprint) and removal (filter lines) are both simpler and more reliable than maintaining a separate state file. |
| Checklist guarded on re-runs | First-time users need the privacy/backup checklist; returning users who've already read it are interrupted unnecessarily; a one-question gate respects their time |
| CLAUDE.md rules written via prose instruction, not a code block | The rules to add depend on runtime user selection and cannot be fully templated; the prose instruction ("write to .tmp, fsync, os.replace") is explicit enough for correct atomic execution |
| Fingerprint-present-without-rule is treated as present | A fingerprint comment in CLAUDE.md without its rule body would cause the rule to be skipped on re-run; fingerprint text is highly specific markdown comment syntax that no user would type manually, making this case effectively impossible |
| Skills overview is hardcoded (not read from README at runtime) | Avoids a file-read tool call at the end of setup; the table is a stable snapshot that changes only when new skills are added to the plugin, at which point this skill should be updated in the same PR |
| `prompt-word-count` hook removed (v0.2.0) | Word count is a bad proxy for ambiguity; the CLAUDE.md rule "ask one clarifying question when ambiguous" handles this without a hook |
