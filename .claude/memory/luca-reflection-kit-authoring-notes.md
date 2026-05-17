# luca-reflection-kit Authoring Notes

- Pure-reasoning agents default to `tools: []` in frontmatter; omit it to grant all tool access (inflating token cost), so add only tools the agent will call.
- Mandate vs output target are independent in multi-agent skills. An agent's mandate (whose patterns it observes) and its output target (where findings land: user-facing display, memory file, skill edit) are separate design choices; state both explicitly in the agent's frontmatter and body. Conflating them produces output aimed at the wrong audience.
- Echo-only `UserPromptSubmit` hooks are intentionally minimal (a single `echo`). Any behavior change must remain side-effect-free (no file writes, no network calls).
- Session logs written by `reflect` go to `~/.claude/reflect-logs/`: this path is user-owned, not plugin-owned. The plugin reads these logs; it does not manage them.
- Any hook surfacing a consent command must instruct Claude to inform the user and wait; auto-invocation coerces acknowledgment.
