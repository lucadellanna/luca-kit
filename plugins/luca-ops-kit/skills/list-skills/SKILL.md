---
name: List Skills
description: List all installed skills with plugin, description, and line count. Trigger on "what skills do I have?", "list skills", or "show available workflows".
version: 0.1.0
---

# List Skills

## Step 1: Discover skill files

Glob for every `SKILL.md`:
- `plugins/<plugin-name>/skills/<skill-name>/SKILL.md`
- `skills/<skill-name>/SKILL.md` (project-root skills)

For each plugin directory, read `.claude-plugin/plugin.json` → `name` and `author.name`.

Note the total count of files found (used in self-reflection).

## Step 2: Build the table

For each file:
1. Read YAML frontmatter: `name:` (fall back to directory name), `description:` (fall back to `—`).
2. Count lines with `wc -l`.
3. Attribution: `<plugin-name> / <author-name>` for plugin skills; `(local)` for project-root.

## Step 3: Present

If zero skills found: say "No skills found. Check that plugins are installed under `plugins/`." Stop.

Otherwise, output sorted by plugin then skill name:

| Skill | Plugin / Author | Description | Lines |
|-------|-----------------|-------------|-------|

End with: `<N> skills found across <M> plugin(s).`

No follow-up questions.

## Self-reflection

Spawn a Haiku sub-agent. Pass it the table, the file count from Step 1, and these criteria:

1. **Completeness** — row count in the table equals the file count noted in Step 1
2. **Accuracy** — description and line count for each row match the file content
3. **Attribution** — every row correctly identifies its plugin or `(local)`

Score each 0–10. If any criterion scores below 8, draft a concise edit to this SKILL.md, show the user, and apply on approval.

## Design decisions

| Decision | Rationale |
|----------|-----------|
| `wc -l` over "count lines" | Removes ambiguity; deterministic across environments |
| Sort by plugin then name | Groups related skills; pure alpha scatters plugin siblings |
| Frontmatter `description:` over body summary | Canonical one-liner; summarising the body risks paraphrasing |
| No search/filter in v0.1 | Sufficient for small libraries; add when list exceeds ~20 skills |
