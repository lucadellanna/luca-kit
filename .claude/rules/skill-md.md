---
paths:
  - "**/SKILL.md"
---

**Child-process variables do not survive to the caller.** When a SKILL.md instructs Claude to run an external script (`bash script.sh`) and then use values from it (for caching, reviewer prompts, or comparisons), those values must appear in the script's stdout output. Variables the script sets internally (e.g. `PROJECT_CLAUDE="$(pwd)/CLAUDE.md"`) are not visible to the orchestrator. Either include the value in the script's output, or re-derive it in the caller from known fixed paths.

**Version bump on meaningful change.** Bump the SKILL.md frontmatter version after every meaningful change: patch (0.x.y to 0.x.y+1) for fixes or additions to existing steps; minor (0.x.0 to 0.x+1.0) for new steps added. The version field is what the Claude plugin system uses to signal an update to cached users.

**Orchestrator steps outside bash blocks.** Write orchestrator action steps as prose outside code blocks, using blocks only for bash syntax examples. Instructions inside `#` comments in a bash block may be treated as inactive by the orchestrator.
