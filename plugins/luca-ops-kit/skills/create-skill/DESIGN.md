# Design decisions

| Decision | Rationale |
|----------|-----------|
| 8 default criteria in Step 2 (exceeds the 2–5 guideline) | Defaults are a menu, not a mandate; users confirm and trim to 2–5 in the Step 2 conversation; a richer starting menu produces better criteria choices than a shorter one |
| Plan mode used for blueprint (Step 3), not a plain AskUserQuestion | EnterPlanMode enforces that Claude cannot write any files or run commands until the user explicitly approves; a plain confirmation question is bypassable if the skill drifts into drafting early |
| Two extra questions in Step 1 (persona, trigger) | Who uses the skill determines tone; the trigger shapes the entry point of the generated skill. Both are lost if not captured before drafting because the user rarely volunteers them unprompted |
| Sonnet (not Haiku) for scoring sub-agents | Step 2 criteria include instruction explicitness and design decision coverage, which require simulating execution paths; Haiku misses subtle precision gaps in these areas |
| Self-reflection is one-shot (no average loop) | The self-reflection checks runtime quality of the generated skill, not the document quality of create-skill itself; document quality is iterated in Step 5; a second loop would conflate the two checks |
| code-reviewer runs before save (Step 6) | Catches injection, boundary, redundant-state, and contradiction bugs that prose-level review misses; placed before save so the user approves the technically verified version |
| audit-skill runs after save (Step 8) | Skills start life with a quality score rather than waiting for a future audit-skills rotation; co-installed as part of the same plugin so almost always available |
| Doc-sync runs after audit (Step 9), not before | The final audited name and description are the ones worth adding to docs; syncing before the audit could register a name or description that still changes |
| Step 9 appends to existing sections only, never creates one | If neither README nor CLAUDE.md has a skills section the project hasn't opted into that convention; imposing structure would be overreach |
| Design decisions stored in DESIGN.md, not SKILL.md | SKILL.md is loaded on every skill execution; DESIGN.md is only needed during audits and code review. Separating them prevents audit rationale from inflating runtime token cost, which compounds as rationale accumulates. |
