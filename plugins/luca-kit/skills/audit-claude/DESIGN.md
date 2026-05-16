# Design decisions

Only non-intuitive choices documented here. Defaults and common-sense choices live in `SKILL.md`.

| Decision | Rationale |
|----------|-----------|
| Sub-agents read the file themselves (`tools: [Read]`) instead of orchestrator passing content via prompt | Differs from luca-reflection-kit's `tools: []` + inline-content convention. For any CLAUDE.md larger than the Read tool definition (always true in practice), reading in-agent is cheaper in total tokens and keeps file content out of the orchestrator's main context. |
| Sonnet for structural, Haiku for micro-compression in parallel | Sonnet gravitates toward judgment-heavy structural findings and skips sentence-level mechanics. A dedicated narrow Haiku prompt catches what Sonnet leaves behind, at no added latency. |
| No upfront user approval; orchestrator applies all findings automatically; verifier catches accidents | The skill exists to REMOVE cruft. Asking the user to approve each finding bottlenecks the value and converts deliberate removals into judgment calls the user does not want to make. Trust model: reviewers propose, orchestrator applies, verifier safety-nets. The user only steps in if the verifier flags something important. |
| Memory move-outs auto-applied only to the co-located memory directory (`./CLAUDE.md` uses `./.claude/memory/`, `~/.claude/CLAUDE.md` uses `~/.claude/memory/`); non-memory targets stay as advice | Memory directories co-located with each CLAUDE.md have unambiguous scope. Non-memory targets (skills, hooks, path rules) require user judgment about the right destination. |
| Verifier flags only "load-bearing" loss, not any content change | The skill's PURPOSE is content removal. The verifier exists to catch ACCIDENTAL loss of rule-application info, not to police every deletion. A reviewer or verifier that defends every word would neuter the skill. The bar is functional: would a reader applying the rule make a different decision because of the change? |
| Restoration is all-or-nothing (`cp` from `/tmp` cache), not per-item | Per-item restoration of memory move-outs requires coordinated multi-file undo (re-insert into CLAUDE.md + remove from memory file). All-or-nothing keeps the safety net deterministic. The reviewers and verifier are calibrated tightly enough that flagged-and-restore should be rare. |
| Cache to `/tmp/audit-claude-project-orig.md` and `/tmp/audit-claude-global-orig.md` (suffix-separated, no path hashing) | Two fixed cache paths avoid collision between the project and global files without needing path hashing. |
| No self-reflection scoring loop | luca-kit's runtime principle is "lightweight, never block". The verifier sub-agent already handles the safety question; a scoring loop on top would gate-on-itself with no new signal. |
