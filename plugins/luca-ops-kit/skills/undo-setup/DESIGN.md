# Design decisions

| Decision | Rationale |
|----------|-----------|
| Manifest as source of truth (not re-scanning) | Re-scanning for fingerprints is fragile if the user edited CLAUDE.md; the manifest records exactly what was added |
| Dedicated lock file (`settings.json.lock`) for flock synchronization | Same reason as in luca-ops-recommended-setup: `fcntl.flock` locks an inode; after `os.replace()` new openers get the new inode with no lock; a persistent `.lock` file ensures synchronization across replacements |
| Hook removal filters within entries, not whole entries | A UserPromptSubmit entry can contain multiple hook objects; dropping the entire entry when one hook matches would silently remove unrelated hooks the user or another tool added to the same entry |
| Remove empty section header after rule removal | Leaves CLAUDE.md clean; a dangling `## Suggested defaults (luca-ops-kit)` header with no content would confuse future audits |
| `rmdir` with `|| true` for luca-ops-kit directory | Only removes the directory if empty (won't accidentally delete user-added files); error suppression is intentional |
| Hooks take effect next session | Platform constraint; user is told explicitly so they know the session they're in still has the hooks active |
| Inline Python/Bash blocks are execution instructions, not user content | Extracting these to external script files would create a file dependency that breaks the skill's self-containment; Claude executes the blocks directly via Bash; the user never sees them |
| Step 2 preview uses manifest text, not live CLAUDE.md state | Verifying live state would add a Read call and create a preview/execute inconsistency if the file changed between preview and execution; Step 3's "absent" reporting handles any drift gracefully |
| Step 2 hook command entry constructed from known pattern, not read from settings.json | The command is always `bash ~/.claude/hooks/<name>.sh`; reading settings.json live would add a tool call and could show a user-modified entry that undo-setup would remove by exact command match regardless |
| Hook removal uses exact command string, not substring | `h.get("command") == f"bash ~/.claude/hooks/{script_name}"` removes only what this plugin installed; substring check risks false positives if another hook command contains the script name as a substring |
| `fcntl` used without Windows fallback | The plugin uses bash `.sh` scripts, `chmod`, and other Unix-only primitives throughout; Windows is not a supported platform |
| Fingerprint-not-found triggers a passive note, not a confirmation gate | If a fingerprint is absent from CLAUDE.md, the rule is already gone; the desired end state is already reached; requiring confirmation would add friction with no safety benefit |
| Completeness and Cleanliness are distinct, not overlapping | Completeness = every manifest item was attempted; Cleanliness = no residue remains in the end state; a run can be complete but leave residue (partial write), or clean but incomplete (missing manifest entry) |
| `null` `UserPromptSubmit` silently treated as empty list (not an error) | If the value is null, no hooks exist to remove; the desired end state is already reached; modifying the file when no changes are needed adds risk with no benefit |
| Step 2 shows fingerprint only, not full rule text | Rule text is not stored in the manifest; reading CLAUDE.md live would contradict the "manifest as source of truth" design decision; the fingerprint (`<!-- luca-ops-kit:{rule-id} -->`) contains the rule ID which is sufficient for user confirmation |
| Hook ID-to-filename mapping duplicated inline in Step 5 header | The table in Step 4 is authoritative; the Step 5 inline note ensures `<name>` is unambiguous when reading Step 5 in isolation, avoiding a cross-step lookup under time pressure |
