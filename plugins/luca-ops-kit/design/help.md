# Design decisions

| Decision | Rationale |
|----------|-----------|
| Dynamic disk reads instead of hardcoded list | Plugin changes frequently; a hardcoded list drifts silently. Extra tool calls are cheap compared to stale help output. |
| Includes itself in the listing | A complete inventory helps users share the full command list with colleagues. Excluding itself would make the table incomplete. |
| Truncates descriptions to first sentence | Frontmatter descriptions vary in length; one sentence keeps the table scannable. |
| Points to `/luca-ops-kit:list-skills` for cross-plugin view | This command only lists its own plugin's items. The existing `list-skills` skill covers all installed plugins; a pointer avoids duplicating that logic. |
| Skills section header says "Claude applies these as part of workflows" | Distinguishes skills from commands for non-technical users who may not understand the difference. Both are invocable via slash command, but skills may also trigger contextually. |
