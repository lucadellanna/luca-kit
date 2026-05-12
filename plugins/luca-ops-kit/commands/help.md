---
description: Show all luca-ops-kit commands and skills with descriptions and examples.
---

Resolve `${CLAUDE_PLUGIN_ROOT}` to the absolute path of this plugin. Run the Bash command below with `PLUGIN` set to that path. Present the output verbatim; no additional commentary.

```bash
PLUGIN="${CLAUDE_PLUGIN_ROOT}"

printf "## luca-ops-kit\n\nLightweight AI operating kit for non-technical companies. Guided meta-skills for turning business procedures, SOPs, and operating knowledge into reusable Claude workflows.\n\n### Commands\n\n"

for f in "$PLUGIN/commands"/*.md; do
  [ -f "$f" ] || continue
  name=$(basename "$f" .md)
  [ "$name" = "help" ] && continue
  section=$(awk '/^## Help$/{found=1;next} found && /^## /{exit} found{print}' "$f" | awk 'NF{p=1} p')
  [ -n "$section" ] && printf "%s\n\n" "$section"
done

printf "### Skills\n\n"
for d in "$PLUGIN/skills"/*/; do
  [ -d "$d" ] || continue
  h="${d}HELP.md"
  [ -f "$h" ] && printf '%s\n\n' "$(cat "$h")"
done
```
