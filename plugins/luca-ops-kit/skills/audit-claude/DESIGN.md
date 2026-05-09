# Design decisions

| Decision | Rationale |
|----------|-----------|
| Line count instead of conciseness score | Line count is objective and instantly comparable; a score requires a sub-agent call per file before the user has even chosen what to audit |
| Single subagent sees all files together | Cross-file redundancy requires joint analysis; sequential per-file scoring misses it |
| Sonnet for analysis (not Haiku) | Identifying load-bearing content vs. bloat requires judgment; Haiku risks flagging necessary context as redundant |
| Haiku for post-write verification | Safety check is pattern-matching (find what was removed), not judgment; Haiku is sufficient and cheaper |
| Single approval for all changes | Reduces friction; the post-write Haiku provides a safety net that makes per-change approval unnecessary |
| Scope check applied at discovery (Step 1) and enforced again at write (Step 6) | Out-of-scope files are excluded before being read or sent to a sub-agent; the write guard is belt-and-suspenders, not the primary control |
| Conductor workspace memories excluded from scope | `~/.claude/projects/*/memory/MEMORY.md` spans all past workspaces including closed ones; ephemeral and not load-bearing |
| Files read by sub-agents, not main context (Steps 4 and 7) | Avoids loading file contents into the main context window; all source material stays in sub-agent contexts, reducing context pollution across long audit runs |
| Originals cached to `/tmp/` with MD5-hashed filenames before Step 6 writes | Enables Haiku verification without holding original content in the main context; MD5 of the full path is collision-free across files that share a basename (e.g. `~/.claude/CLAUDE.md` vs `./CLAUDE.md`) |
| POSIX tools assumed (`/tmp/`, md5/md5sum) | Claude Code runs on macOS and Linux; Windows is out of scope for this skill |
| Parallel Haiku micro-compression pass (Step 4B) | Sonnet gravitates toward structural/cross-file findings and misses sentence-level compression; a dedicated Haiku pass with a narrow prompt catches what Sonnet leaves behind, at no extra latency since both run in parallel |
