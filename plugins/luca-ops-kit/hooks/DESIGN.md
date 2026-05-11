# hooks/DESIGN.md

Design decisions for `claude-md-tidy.sh` and `hooks.json`.

## eval + shlex.quote() pattern

The hook uses a pattern like:
```bash
eval "$(python3 -c "import shlex, sys; ..." <<< "$input")"
```

This is intentional and safe: `shlex.quote()` escapes all values before `eval` runs. No unescaped user content is ever interpolated into the evaluated string, so there is no injection surface. Alternative patterns (heredocs, passing via env vars) are more verbose without adding safety.

## Silent exit on python3 failure

If `python3` is unavailable or fails, the hook exits silently rather than printing an error. Rationale: hooks run after every Edit/Write; a loud error on every file save would break the user's session. A missing Python3 is a setup issue, not a per-invocation runtime concern.

## Metrics as approximations

`duplicate_lines`, `word_count`, and similar metrics are intentional approximations to guide review, not precision measurements. Structural elements (table separators, blank lines, comment markers) are excluded where feasible, but edge cases exist. The goal is to surface obvious bloat, not to enforce a hard threshold.

## hooks.json location

`hooks.json` lives in the `hooks/` subdirectory alongside `claude-md-tidy.sh`, not at the plugin root. This is the correct Conductor plugin convention. Verified against the official Vercel plugin at `~/.claude/plugins/cache/claude-plugins-official/vercel/0.42.1/hooks/hooks.json`, which uses an identical `hooks/` subdirectory layout.
