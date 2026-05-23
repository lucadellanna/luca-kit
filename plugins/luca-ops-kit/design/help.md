# Design decisions

| Decision | Rationale |
|----------|-----------|
| Dynamic disk reads instead of hardcoded list | Plugin changes frequently; a hardcoded list drifts silently. Extra tool calls are cheap compared to stale help output. |
| Includes itself in the listing | A complete inventory helps users share the full command list with colleagues. Excluding itself would make the table incomplete. |
| Truncates descriptions to first sentence | Frontmatter descriptions vary in length; one sentence keeps the table scannable. |
| Points to `/luca-kit:list-skills` for cross-plugin view | This command only lists its own plugin's items. The existing `list-skills` skill covers all installed plugins; a pointer avoids duplicating that logic. |
| Skills section header says "Claude applies these as part of workflows" | Distinguishes skills from commands for non-technical users who may not understand the difference. Both are invocable via slash command, but skills may also trigger contextually. |
| Plugin description is hardcoded in the printf statement | The description is a stable one-liner that describes the plugin's identity; it is not read from plugin.json to avoid an extra file read. It should only change when the plugin's fundamental purpose changes, at which point both the printf and plugin.json would be updated in the same commit. |
| Uses `${CLAUDE_PLUGIN_ROOT}` not hardcoded relative paths | Plugin installs at different paths on different machines. Hardcoded paths like `plugins/luca-ops-kit/` would break on user installs. `${CLAUDE_PLUGIN_ROOT}` is the standard plugin variable for this. |
| Low line-read limits (5 for commands, 10 for skills) | This plugin's frontmatter is consistently short (description on line 2-3, name on line 2-4). Reading 20 lines would waste tokens. If frontmatter grows, increase the limit then. |
