---
paths:
  - "plugins/*/agents/*.md"
---

**Plugin agent file location.** Agent files go in `agents/<name>.md` at the plugin root, not inside a skill's subdirectory; the file IS the agent's prompt (frontmatter + body = system prompt).

**No coverage quotas in agent prompts.** Never add "if fewer than N% of items are flagged, double-check" instructions; threshold-based completeness checks pressure the model to manufacture low-quality findings to satisfy the quota. State the exhaustive enumeration requirement directly ("enumerate every X; do not stop at first match") without a numeric threshold.
