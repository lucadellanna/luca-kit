# Design decisions: bump-on-pr-create.sh

## JSON passed via here-string, not env var

`COMMAND=$(python3 ... <<< "$INPUT")` uses a bash here-string rather than `INPUT="$INPUT" python3`.

**Why:** Claude Code hook payloads can be large (full command text). Env vars hit `MAX_ARG_STRLEN` (~128 KB on Linux), which would silently truncate or error. Here-strings are written to a temp file by bash and are not subject to that limit. The code-review checklist also explicitly prefers here-strings over env vars for this reason.
