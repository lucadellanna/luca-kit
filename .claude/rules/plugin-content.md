---
paths:
  - "**/SKILL.md"
  - "**/REQUIREMENTS.md"
  - "**/DESIGN.md"
  - "**/checklists/*.md"
---

**Plugin-internal references use `${CLAUDE_PLUGIN_ROOT}`, not repo-relative paths.** Inside markdown content (SKILL.md, REQUIREMENTS.md, DESIGN.md, checklists), any reference to the plugin's own files must use `${CLAUDE_PLUGIN_ROOT}/<rest-of-path>` (repo-relative paths only work in the source repo; after `claude plugin install`, they no longer resolve).
