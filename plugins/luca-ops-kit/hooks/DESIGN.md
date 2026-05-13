# hooks/DESIGN.md

Design decisions for `claude-md-tidy.sh` and `hooks.json`.

## eval + shlex.quote() pattern

The hook uses a pattern like:
```bash
eval "$(python3 -c "import shlex, sys; ..." <<< "$input")"
```

This is intentional and safe: `shlex.quote()` escapes all values before `eval` runs. No unescaped user content is ever interpolated into the evaluated string, so there is no injection surface.

**stdin (here-string) over env var:** The JSON input is passed via `<<< "$input"` (bash here-string), not via an env var. This is deliberate: bash here-strings have no size limit, while env vars are subject to `ARG_MAX` on Linux (typically ~128 KB when combined with other env vars). Hook input can be large (e.g. a full file rewrite). Passing large data via env var risks silent truncation or failure. The here-string approach is safer for unbounded inputs.

## Silent exit on python3 failure

If `python3` is unavailable or fails, the hook exits silently rather than printing an error. Rationale: hooks run after every Edit/Write; a loud error on every file save would break the user's session. A missing Python3 is a setup issue, not a per-invocation runtime concern.

## Metrics as approximations

`duplicate_lines`, `word_count`, and similar metrics are intentional approximations to guide review, not precision measurements. Structural elements (table separators, blank lines, comment markers) are excluded where feasible, but edge cases exist. The goal is to surface obvious bloat, not to enforce a hard threshold.

## MultiEdit tool_input structure

In Claude Code's `MultiEdit` tool, `file_path` is a per-edit key nested inside each object in the `edits` list, not at the top level of `tool_input`. The hooks iterate `inp.get("edits", [])` and extract `edit.get("file_path")` from each item. This has been verified against live tool payloads.

## Bash write-op heuristic: redirect-direction check

Naively checking "does the command contain a rule file AND a redirect operator?" produces false positives for read operations like `cat CLAUDE.md > backup.md`. The hooks instead extract the substring after the last `>` (`cmd[cmd.rfind(">") + 1:]`) and check whether the rule file appears in that right-hand side. This correctly identifies the destination file without full shell parsing. Known limitation: highly unusual multi-redirect constructs (e.g., process substitution) may be misjudged, but these do not appear in normal Claude tool use.

## hooks.json location

`hooks.json` lives in the `hooks/` subdirectory alongside `claude-md-tidy.sh`, not at the plugin root. This is the correct Conductor plugin convention. Verified against the official Vercel plugin at `~/.claude/plugins/cache/claude-plugins-official/vercel/0.42.1/hooks/hooks.json`, which uses an identical `hooks/` subdirectory layout.
