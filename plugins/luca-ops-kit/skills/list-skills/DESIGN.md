# Design decisions

| Decision | Rationale |
|----------|-----------|
| Embedded Python script for Steps 1–2 | 159 skills = 159 Read calls without a script; 2 Bash calls with one. Batch wins at any scale. |
| Latest version only for cached plugins | Multiple cached versions create duplicate rows; only the active version matters to the user |
| Skip `upstream/` subdirectories | These are upstream copies stored for diffing, not active skills |
| `~/.claude/skills/` via Python `os.listdir` | Glob tool may not reach this path due to sandbox restrictions; Python bypasses this |
| Frontmatter `description:` over body summary | Canonical one-liner; summarising the body risks paraphrasing |
| Sort by plugin then name | Groups related skills; pure alpha scatters plugin siblings |
| No search/filter in v0.2 | Sufficient for current scale; add when user asks |
| Raw mode exits after Step 1 | Skills that consume structured data don't need the rendered table; raw mode keeps list-skills DRY while supporting both use cases |
