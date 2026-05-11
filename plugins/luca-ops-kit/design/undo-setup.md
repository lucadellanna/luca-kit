# Design decisions

| Decision | Rationale |
|----------|-----------|
| Fingerprints as source of truth (not manifest) | Rules are self-identifying via `<!-- luca-ops-kit:... -->` comments. Grepping CLAUDE.md directly is simpler and more reliable than maintaining a separate `applied.json` manifest. If a user manually deleted a rule, the fingerprint is gone and the rule is correctly treated as already removed. |
| No settings.json writes | Hooks moved to plugin-level `hooks.json` in v0.3.0; they auto-uninstall with the plugin. `undo-setup` only needs to remove CLAUDE.md rules. |
| Remove empty section header after rule removal | Leaves CLAUDE.md clean; a dangling `## Suggested defaults (luca-ops-kit)` header with no content would confuse future audits |
| `rmdir` with `\|\| true` for luca-ops-kit directory | Only removes the directory if empty (won't accidentally delete user-added files); error suppression is intentional |
| Inline Python/Bash blocks are execution instructions, not user content | Extracting these to external script files would create a file dependency that breaks the skill's self-containment; Claude executes the blocks directly via Bash; the user never sees them |
| Fingerprint-not-found triggers a passive note, not a confirmation gate | If a fingerprint is absent from CLAUDE.md, the rule is already gone; the desired end state is already reached; requiring confirmation would add friction with no safety benefit |
| Cleans up old `applied.json` if present | Future-proofs against the possibility that an `applied.json` from a previous version exists; removing it prevents stale state from confusing future runs |
