---
paths:
  - "**/SKILL.md"
---

**Child-process variables do not survive to the caller.** When a SKILL.md instructs Claude to run an external script (`bash script.sh`) and then use values from it (for caching, reviewer prompts, or comparisons), those values must appear in the script's stdout output. Variables the script sets internally (e.g. `PROJECT_CLAUDE="$(pwd)/CLAUDE.md"`) die when the process exits and are never visible to the orchestrator. Either include the value in the script's output, or re-derive it in the caller from known fixed paths.
