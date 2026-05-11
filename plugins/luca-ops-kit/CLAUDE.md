# luca-ops-kit

Runtime instructions active whenever this plugin's skills are in use.

## First-run

**Disclaimer (once per install):** At the very start of the session, before addressing any other request (skip if `mode: raw` is present in the opening message), check if `~/.claude/luca-ops-kit/disclaimer-v1.0-shown` exists. If it does not:
1. Run `cat "$CLAUDE_PLUGIN_ROOT/DISCLAIMER.md"` and display the output verbatim.
2. Run `mkdir -p ~/.claude/luca-ops-kit && echo "v1.0 shown $(date +%Y-%m-%d)" > ~/.claude/luca-ops-kit/disclaimer-v1.0-shown`
3. Do not display it again this session.

**Setup prompt:** After the disclaimer (if shown), before addressing any other request, if neither `~/.claude/luca-ops-kit/setup-complete` nor `~/.claude/luca-ops-kit/applied.json` exists, suggest running `/luca-ops-recommended-setup`. On a fresh install where both apply, show the disclaimer first, then the setup suggestion in the same response. If the user declines setup, do not suggest it again this session.

## Audience

Users are non-technical staff inside partner companies. Skills must use plain language, guide users step-by-step, and never assume technical fluency.

**Personas: calibrate tone and assumed knowledge accordingly:**

| Persona | Typical use |
|---------|------------|
| Manager | Identifies what should become a skill; points the toolkit at a procedure |
| Admin | Turns a repeated reporting task into a reusable workflow |
| Salesperson | Converts a successful call-prep or outreach process into a skill |
| Frontline manager | Builds an SOP from tacit know-how before knowledge walks out the door |
| Local power user | Audits, consolidates, improves, and governs the team's skill library |

**Scope guardrail:** improve productivity, consistency, training, documentation, and low-stakes decision support. Never automate high-stakes decisions; always include human approval points for consequential outputs.

**Meta-skill triggers:** always explicit by name (e.g., `/create-skill`, `/reflect`). Never task-context triggered.

## Principles

- **Plain language.** No jargon. If a term needs explanation, explain it inline. Exception: Claude-native terms and model/agent directives used as instructions to Claude (e.g., `AskUserQuestion`, `multiSelect`, model tier references, sub-agent spawning instructions) are acceptable in SKILL.md files; they are directives for Claude, not content shown to users.
- **Guided workflows.** Skills walk users through steps. Never dump options without context.
- **No unvalidated assumptions.** If a skill must assume something about the user's context, state the assumption and ask the user to confirm before proceeding.
- **Human approval points.** High-stakes outputs require explicit user confirmation before acting.
- **Guardrails against overreach.** Skills stay within their stated scope. Flag when a request falls outside.
- **Token efficiency.** Minimize token use. Short sentences, no redundant context, no verbose output formatting.
- **Match quality machinery to output type.** Skills producing durable artifacts (files, configs, scripts) that must work standalone warrant sub-agent scoring loops before presenting. Skills producing ephemeral, user-judged output (insights, suggestions, analysis) present immediately and let the user react. Do not add iteration loops, structured data schemas, or multi-agent pipelines preemptively for future consumers that may never materialise or whose needs will change.
- **Self-reflection.** Every skill that produces durable artifacts includes a `## Self-reflection` section: 2–5 MECE success criteria scored 0–10 by a Haiku sub-agent. If average < 9.5, revise and re-score (max 3 iterations; stop if score plateaus). If any criterion remains below 8 after iteration, draft a concise edit to this SKILL.md to prevent the same failure, show it to the user, and apply on approval. Skills producing ephemeral, user-judged output may omit this section; document the omission in DESIGN.md.
- **Self-observation.** During skill execution, log problems encountered (unexpected behavior, wasted iterations, tool failures, scorer inconsistencies, unnecessary context pollution) to a running task list. After the main work completes, investigate each item for root cause and decide whether a permanent fix is needed (skill edit, CLAUDE.md rule, audit-skill change). Apply fixes before closing the task. Context pollution check: for every `Read` or `Bash cat` call, verify the content was needed in the model's context; if a script could have operated on the file directly without loading it, flag it.
- **Scoring is net of design decisions.** Every skill directory may include a `DESIGN.md` file documenting intentional trade-offs. Scoring sub-agents must treat documented decisions as accepted; do not penalise them. When an audit raises a concern that is deliberately accepted (not overlooked), add it to `DESIGN.md` rather than leaving it as an open gap.
- **DESIGN.md stays current.** When a code change affects the rationale for a decision, update `DESIGN.md` in the same edit; never as a follow-up. A stale rationale is a contradiction, not documentation.

## Inter-skill patterns

- **Raw-mode data contract.** When a skill produces output another skill may need to consume as structured data, add a `mode: raw` clause at the top of the skill body: if `mode: raw` is passed in the opening message, return TSV/JSON and skip rendering. Never embed another skill's script inline; invoke in raw mode instead.
- **Absolute paths in data output.** When a skill emits file paths as structured data (TSV, JSON), always normalize with `os.path.abspath()`. The consuming skill may run from a different working directory, so relative paths silently break the data contract.
- **Sanitize at the boundary.** When emitting structured output (TSV, CSV, JSON), do all field escaping in a single pass at the output statement. Never scatter sanitization across helper functions: fields added later skip it and review catches the gap one field at a time.
- **Manifest-as-source-of-truth for global-state writes.** When a skill writes to global state in multiple steps, record each write to a plugin-namespaced manifest (e.g., `~/.claude/<plugin>/applied.json`) before marking setup complete. The companion undo skill reads only the manifest; never re-scans user files; this ensures precise, safe reversal.
- **Typed agent spawns vs. model-tier spawns.** Skills may use either `subagent_type: <agent-type>` (a specialized agent with defined tools, e.g. `feature-dev:code-reviewer`) or a generic model-tier spawn (e.g. "spawn a Haiku sub-agent"). These are different primitives. Do not replace a typed agent spawn with a generic model tier: specialized agents have capabilities generic spawns lack. Automated reviewers (Gemini) may flag typed agent names as non-standard; pre-classify such suggestions as false positives unless the agent type does not exist in this environment.
