# luca-ops-kit

Meta-workflow toolkit that helps non-technical organizations turn recurring tasks, SOPs, wiki pages, and managerial know-how into reusable Claude Skills. Ships structured workflows for building skills, auditing them, extracting procedures, creating company context, and setting explicit success criteria, red flags, human approval points, and decision boundaries. Domain skills (the actual business procedures) are added by holding companies on top of this base layer.

## Audience

Users are non-technical staff inside partner companies. Skills must use plain language, guide users step-by-step, and never assume technical fluency.

**Personas — calibrate tone and assumed knowledge accordingly:**

| Persona | Typical use |
|---------|------------|
| Manager | Identifies what should become a skill; points the toolkit at a procedure |
| Admin | Turns a repeated reporting task into a reusable workflow |
| Salesperson | Converts a successful call-prep or outreach process into a skill |
| Frontline manager | Builds an SOP from tacit know-how before knowledge walks out the door |
| Local power user | Audits, consolidates, improves, and governs the team's skill library |

**Scope guardrail:** improve productivity, consistency, training, documentation, and low-stakes decision support. Never automate high-stakes decisions — always include human approval points for consequential outputs.

**Layer model:**
- **luca-ops-kit (this plugin):** meta-skills only — the toolkit for building and improving procedures
- **Holdco layer:** domain skills curated for a specific industry or portfolio (holding companies, investors, franchisors, trade associations, operating groups)
- **Partner company:** uses both layers; adapts holdco domain skills to their local context

## Skill categories

All skills in this plugin are meta-skills. When adding a skill, confirm it fits the meta layer: build, govern, or improve procedures — not encode a specific business procedure.

**Meta-skill triggers:** always explicit by name (e.g., `/create-skill`, `/reflect`). Never task-context triggered. Audience: anyone wanting to build or improve the team's skill library.

## Structure

```
.claude-plugin/plugin.json   # Plugin manifest
skills/<name>/SKILL.md        # One directory per skill
```

Skill directories use kebab-case verb-noun names (e.g., `review-invoice`, `onboard-client`).

No commands, agents, or hooks yet — skills only.

## Principles

- **Plain language.** No jargon. If a term needs explanation, explain it inline. Exception: Claude-native terms and model/agent directives used as instructions to Claude (e.g., `AskUserQuestion`, `multiSelect`, model tier references, sub-agent spawning instructions) are acceptable in SKILL.md files — they are directives for Claude, not content shown to users.
- **Guided workflows.** Skills walk users through steps. Never dump options without context.
- **No unvalidated assumptions.** If a skill must assume something about the user's context, state the assumption and ask the user to confirm before proceeding.
- **Human approval points.** High-stakes outputs require explicit user confirmation before acting.
- **Guardrails against overreach.** Skills stay within their stated scope. Flag when a request falls outside.
- **Token efficiency.** Minimize token use. Short sentences, no redundant context, no verbose output formatting.
- **Self-reflection.** Every skill includes a `## Self-reflection` section: 2–5 MECE success criteria scored 0–10 by a Haiku sub-agent. If average < 9.5, revise and re-score (max 3 iterations; stop if score plateaus). If any criterion remains below 8 after iteration, draft a concise edit to this SKILL.md to prevent the same failure, show it to the user, and apply on approval.
- **Scoring is net of design decisions.** Every skill may include a `## Design decisions` section documenting intentional trade-offs. Scoring sub-agents must treat documented decisions as accepted — do not penalise them. When an audit raises a concern that is deliberately accepted (not overlooked), add it to `## Design decisions` rather than leaving it as an open gap.

## Inter-skill patterns

- **Raw-mode data contract.** When a skill produces output another skill may need to consume as structured data, add a `mode: raw` clause at the top of the skill body: if `mode: raw` is passed in the opening message, return TSV/JSON and skip rendering. Never embed another skill's script inline; invoke in raw mode instead.
- **Complex skill review.** Before writing the first line of a complex skill (multi-step orchestration, state management, inter-skill delegation), run two independent Sonnet review passes on the plan; each reviewer starts with no conversation context. This reliably surfaces issues that in-context review misses.
- **Absolute paths in data output.** When a skill emits file paths as structured data (TSV, JSON), always normalize with `os.path.abspath()`. The consuming skill may run from a different working directory, so relative paths silently break the data contract.
- **Sanitize at the boundary.** When emitting structured output (TSV, CSV, JSON), do all field escaping in a single pass at the output statement. Never scatter sanitization across helper functions: fields added later skip it and review catches the gap one field at a time.
- **Gitignore generated state files.** When a skill generates a local state or cache file, add it to `.gitignore` immediately; do not leave it as a "you should" note in the skill doc. The skill's note can then confirm it is already excluded rather than instructing the user to exclude it.
- **Incremental-edit Sonnet gate.** When a complex skill (multi-step orchestration, state management, inter-skill delegation) receives 3 or more incremental edits in one session, run one final independent Sonnet pass on the complete updated file before committing. In-context incremental review misses step-sequence bugs and edge cases that accumulate across edits.
