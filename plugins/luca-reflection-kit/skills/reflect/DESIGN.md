# Design decisions

| Decision | Rationale |
|----------|-----------|
| No sub-agent scoring loop before presenting | Reflect produces ephemeral, user-judged output (insights). The user is present and can judge quality instantly; sub-agent scoring adds latency without value. Scoring loops are for durable artifacts that must work standalone. |
| No self-reflection section | A self-reflection step inside a reflection skill is recursion without termination value. The user's response to findings IS the quality signal. |
| Trivial logging (date + finding strings) | Previous version had 60-line Python with FK relationships, finding IDs, memory_target fields, and duplicate-date guards. This coupled reflect tightly to /dream's internals and added latency every session. Simpler format is still parseable; if /dream needs richer data later, that's /dream's problem to solve at consumption time, not reflect's to pre-optimize for. |
| Scan areas are suggestions, not a checklist | Previous version had 7 prescribed areas that forced filler findings. New version lists 4 areas with explicit instruction to skip irrelevant ones. Coverage is not a goal; signal density is. |
| Keep logging opt-in ceremony (Step 0) | Privacy concern: defaulting to logging and mentioning opt-out after the fact may surprise privacy-conscious users. The current approach front-loads consent. Acceptable cost given it only triggers once (dotfile persists). |
| Bash dotfile check, not Glob | Glob excludes dotfiles by default and would silently miss `.enabled`/`.disabled`, re-prompting every session |
| All findings logged, not just acted-on ones | Gap between findings and actions is still useful signal for /dream |
| Python for atomic JSONL append | Single buffered write prevents partial lines from interrupted processes |
