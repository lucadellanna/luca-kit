# luca-ops-kit

Lightweight AI operating kit for non-technical companies. Helps users turn business procedures, SOPs, wiki pages, and operating knowledge into reusable Claude skills.

## Audience

Users are managers, admin staff, salespeople, frontline employees, and executives inside partner companies — not developers. Skills must use plain language, guide users step-by-step, and never assume technical fluency.

A holding company licenses this plugin and curates industry-specific knowledge (procedures, checklists, best practices). Partner companies adapt that knowledge to their local context using the plugin's guided workflows.

## Structure

```
.claude-plugin/plugin.json   # Plugin manifest
skills/<name>/SKILL.md        # One directory per skill
```

Skill directories use kebab-case verb-noun names (e.g., `review-invoice`, `onboard-client`).

No commands, agents, or hooks yet — skills only.

## Principles

- **Plain language.** No jargon. If a term needs explanation, explain it inline.
- **Guided workflows.** Skills walk users through steps. Never dump options without context.
- **No unvalidated assumptions.** If a skill must assume something about the user's context, state the assumption and ask the user to confirm before proceeding.
- **Human approval points.** High-stakes outputs require explicit user confirmation before acting.
- **Guardrails against overreach.** Skills stay within their stated scope. Flag when a request falls outside.
- **Token efficiency.** Minimize token use. Short sentences, no redundant context, no verbose output formatting.
- **Self-scoring loop.** Every skill defines 2–5 success criteria and scores its output 0–10 per criterion before finishing. If average < 9.5, revise and re-score. Stop if score plateaus or after 3 iterations.
