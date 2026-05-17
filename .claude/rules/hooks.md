---
paths:
  - "hooks/*.sh"
  - "hooks/*.py"
  - "hooks/hooks.json"
---

**New hook file touchpoints.** Adding a hook to this repo requires updates in ~10 files: the script itself (`hooks/<name>.sh`), `hooks/hooks.json`, plugin `CLAUDE.md`, plugin `README.md`, `plugin.json`, root `CLAUDE.md`, root `README.md`, `INDEX.md`, `.claude-plugin/marketplace.json`, and (if present) `CHANGELOG.md`. All in one commit per the global "hook and referenced scripts are one deployable unit" rule.
