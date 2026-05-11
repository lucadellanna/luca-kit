---
description: Show all luca-ops-kit commands and skills with descriptions. Use when you want to know what this plugin can do.
---

# luca-ops-kit Help

Show the user what this plugin offers. Read descriptions dynamically from disk so the listing never drifts from reality.

## Step 1: Collect commands

Use Glob to find all `.md` files in `${CLAUDE_PLUGIN_ROOT}/commands/`. For each file except `help.md` (this command), read the first 5 lines and extract the `description` field from the YAML frontmatter. Also extract the filename (without `.md`) as the command name.

## Step 2: Collect skills

Use Glob to find all `SKILL.md` files in `${CLAUDE_PLUGIN_ROOT}/skills/*/`. For each, read the first 10 lines and extract the `name` and `description` fields from the YAML frontmatter. Use the `name` field as the skill name; fall back to the directory name if `name` is missing.

## Step 3: Present

Print a brief intro, then two sections. Use this exact format:

```
## luca-ops-kit

Lightweight AI operating kit for non-technical companies. Guided meta-skills for turning business procedures, SOPs, and operating knowledge into reusable Claude workflows.

### Commands (run explicitly with /luca-ops-kit:<name>)

| Command | Description |
|---------|-------------|
| `/luca-ops-kit:<name>` | <description> |

### Skills (Claude applies these as part of workflows)

| Skill | Description |
|-------|-------------|
| `<name>` | <description> |

---
💡 Use `/luca-ops-kit:list-skills` to see skills from **all** installed plugins.
```

Keep descriptions to one sentence each. If a frontmatter description is longer, truncate to the first sentence.
