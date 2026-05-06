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

All skills in this plugin are meta-skills. When adding a new skill, confirm it fits the meta layer: it should help users build, govern, or improve procedures — not encode a specific business procedure itself.

**Meta-skill triggers:** always explicit by name (e.g., `/create-skill`, `/reflect`). Never task-context triggered. Audience: anyone wanting to build or improve the team's skill library.

## Structure

```
.claude-plugin/plugin.json   # Plugin manifest
skills/<name>/SKILL.md        # One directory per skill
```

Skill directories use kebab-case verb-noun names (e.g., `review-invoice`, `onboard-client`).

No commands, agents, or hooks yet — skills only.

## Principles

- **Plain language.** No jargon. If a term needs explanation, explain it inline. Exception: Claude-native terms used as instructions to Claude (e.g., `AskUserQuestion`, `multiSelect`) are acceptable in SKILL.md files — they are directives for Claude, not content shown to users.
- **Guided workflows.** Skills walk users through steps. Never dump options without context.
- **No unvalidated assumptions.** If a skill must assume something about the user's context, state the assumption and ask the user to confirm before proceeding.
- **Human approval points.** High-stakes outputs require explicit user confirmation before acting.
- **Guardrails against overreach.** Skills stay within their stated scope. Flag when a request falls outside.
- **Token efficiency.** Minimize token use. Short sentences, no redundant context, no verbose output formatting.
- **Self-scoring loop.** Every skill defines 2–5 success criteria and scores its output 0–10 per criterion before finishing. If average < 9.5, revise and re-score. Stop if score plateaus or after 3 iterations.
