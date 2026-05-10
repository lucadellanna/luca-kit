# Design decisions

| Decision | Rationale |
|----------|-----------|
| Criteria table passed to sub-agents in full on each call | Stateless sub-agents have no access to the parent conversation; full context must be provided on every spawn; this is not redundancy |
| No edit-permission check in Step 1 | Skills live in team-owned repositories; the caller is assumed to have appropriate access |
| Sonnet (not Haiku) for scoring sub-agents | Instruction explicitness and criterion ambiguity require simulating execution paths; Haiku scores surface-level clarity but misses subtle precision gaps. Haiku remains appropriate for the self-reflection binary checks. |
| Fix vs. Document classification in Step 3 | Concerns that are inherent trade-offs should become DESIGN.md entries, not code changes; conflating the two causes wasted iteration rounds where the re-scorer flags the same concern again because it isn't yet documented |
| Clarity criterion scoped to user-facing outputs, not SKILL.md text | SKILL.md contains technical instructions for Claude (code blocks, tool names, model directives); penalising these for non-technical readability misapplies the criterion; Token efficiency already judges SKILL.md text length |
| Design-decision pre-check is a mandatory first step in scorer prompt | Placing "score net of documented decisions" as a trailing clause in prose causes scorers to acknowledge it in aggregate but ignore it per-criterion; making it the first explicit step anchors the scorer before any criterion is evaluated |
| DESIGN.md read separately from SKILL.md | Design rationale is only needed during audits, not at runtime; storing it in a companion file keeps SKILL.md lean for the common execution case |
