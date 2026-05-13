# luca-ops-kit

Runtime instructions active whenever this plugin's skills are in use.

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

**Meta-skill triggers:** always explicit by name (e.g., `/create-skill`, `/audit-skill`). Never task-context triggered.

## Principles

- **Plain language.** No jargon. If a term needs explanation, explain it inline. Exception: Claude-native terms and model/agent directives used as instructions to Claude (e.g., `AskUserQuestion`, `multiSelect`, model tier references, sub-agent spawning instructions) are acceptable in SKILL.md files; they are directives for Claude, not content shown to users.
- **Guided workflows.** Skills walk users through steps. Never dump options without context.
- **No unvalidated assumptions.** If a skill must assume something about the user's context, state the assumption and ask the user to confirm before proceeding.
- **Human approval points.** High-stakes outputs require explicit user confirmation before acting.
- **Guardrails against overreach.** Skills stay within their stated scope. Flag when a request falls outside.
- **Token efficiency.** Minimize token use. Short sentences, no redundant context, no verbose output formatting.
- **Match quality machinery to output type.** Skills producing durable artifacts (files, configs, scripts) that must work standalone warrant sub-agent scoring loops before presenting. Skills producing ephemeral, user-judged output (insights, suggestions, analysis) present immediately and let the user react. Do not add iteration loops, structured data schemas, or multi-agent pipelines preemptively for future consumers that may never materialise or whose needs will change.
- **Self-reflection.** Every skill that produces durable artifacts includes a `## Self-reflection` section: 2–5 MECE success criteria scored 0–10 by a Haiku sub-agent. If average < 9.5, revise and re-score (max 3 iterations; stop if score plateaus). If any criterion remains below 8 after iteration, draft a concise edit to this SKILL.md to prevent the same failure, show it to the user, and apply on approval. Two exceptions may omit this section (document the omission in DESIGN.md): (a) skills producing ephemeral, user-judged output; (b) skills whose durable output is itself quality-gated by a dedicated downstream skill (e.g., `audit-skill`), so a self-reflection here would be a duplicate gate on the same artifact.
- **Self-observation.** During skill execution, log problems encountered (unexpected behavior, wasted iterations, tool failures, scorer inconsistencies, unnecessary context pollution) to a running task list. After the main work completes, investigate each item for root cause and decide whether a permanent fix is needed (skill edit, CLAUDE.md rule, audit-skill change). Apply fixes before closing the task. Context pollution check: for every `Read` or `Bash cat` call, verify the content was needed in the model's context; if a script could have operated on the file directly without loading it, flag it.
- **Scoring is net of design decisions.** Every skill directory may include a `DESIGN.md` file documenting intentional trade-offs. Scoring sub-agents must treat documented decisions as accepted; do not penalise them. When an audit raises a concern that is deliberately accepted (not overlooked), add it to `DESIGN.md` rather than leaving it as an open gap.
- **DESIGN.md stays current.** When a code change affects the rationale for a decision, update `DESIGN.md` in the same edit; never as a follow-up. A stale rationale is a contradiction, not documentation.

## Error correction (enforced by plugin hooks)

**Error → rule update (non-negotiable).** Enforced by the plugin's `stop-apology-check.py` Stop hook.

Triggers (any of):
1. Self-correction phrases appear in your output: "you're right", "good catch", "my mistake", "I shouldn't have", "the issue was", "I missed", "I should have", "I apologize", "I apologise".
2. User points out a mistake, inefficiency, or wrong assumption.
3. A tool returns an error, or returns output that wasted a round (looked useful, was not), and the cause is a reusable pattern (wrong invocation, missing setup, predictable failure mode). Single transient failures with no pattern do not trigger.

When triggered, the response must render this widget verbatim before continuing other work. The backticked horizontal-rule lines are required: they make the widget visually distinct and machine-detectable by the Stop hook.

`★ rule-update ─────────────────────────────────`
Error class: <name the class, not the instance>
Rule: <imperative sentence preventing all instances>
Scope: <file to edit, e.g. plugins/<name>/CLAUDE.md | skill <name> | hook <name> | structural (tool/code change needed)>
Edit: <the Edit tool call follows in this same response; machine-enforced: the widget alone without an actual Edit tool call will not pass the Stop hook. If Scope = structural, propose the structural fix and ask before coding.>
`─────────────────────────────────────────────────`

Then append one line to `~/.claude/error-log.md`: `YYYY-MM-DD | <error class> | <file edited or "structural-proposed">`. Create the file if absent. If a rule of this class already exists and was violated, the Edit must tighten it (more explicit triggers, fewer escape hatches), not restate it.

Forbidden evasions (each is a rule violation):
- "the fix is behavioural", "I'll be more careful", "noted for next time", "added to task list", "will remember"
- Asking permission to apply the fix to a rule file
- Deferring the Edit to a later turn

One-off escape valve: if the error is genuinely unpredictable and not a class (single typo, no pattern), say so explicitly in one sentence of why no rule applies. Silent skipping is non-compliance.

**Rules must use tight, imperative language.** Enforced by the plugin's `hedge-scan.py` PostToolUse hook on list-item lines in rule-like file paths. Use direct commands with no escape hatches ("never", "always", "apply immediately"). Hedged language ("try to", "consider", "prefer", "should probably") creates rationalization space and will be exploited. If a rule has been violated despite existing, rewrite it to be tighter, not just more emphatic.

## Inter-skill patterns

- **Raw-mode data contract.** When a skill produces output another skill may need to consume as structured data, add a `mode: raw` clause at the top of the skill body: if `mode: raw` is passed in the opening message, return TSV/JSON and skip rendering. Never embed another skill's script inline; invoke in raw mode instead.
- **Absolute paths in data output.** When a skill emits file paths as structured data (TSV, JSON), always normalize with `os.path.abspath()`. The consuming skill may run from a different working directory, so relative paths silently break the data contract.
- **Sanitize at the boundary.** When emitting structured output (TSV, CSV, JSON), do all field escaping in a single pass at the output statement. Never scatter sanitization across helper functions: fields added later skip it and review catches the gap one field at a time.
- **Prefer self-identifying artifacts over manifests.** When a skill writes artifacts that can be detected by their content (e.g., fingerprinted lines in a config file), use detection-based undo rather than maintaining a separate manifest. Only use a manifest when artifacts are not self-identifying (e.g., binary files, entries without distinguishing markers).
- **Typed agent spawns vs. model-tier spawns.** Skills may use either `subagent_type: <agent-type>` (a specialized agent with defined tools, e.g. `feature-dev:code-reviewer`) or a generic model-tier spawn (e.g. "spawn a Haiku sub-agent"). These are different primitives. Do not replace a typed agent spawn with a generic model tier: specialized agents have capabilities generic spawns lack. Automated reviewers (Gemini) may flag typed agent names as non-standard; pre-classify such suggestions as false positives unless the agent type does not exist in this environment.
- **Cross-cutting rules in checklists, not inlined at each site.** When the same rule would otherwise be stated in multiple SKILL.md or REQUIREMENTS.md files, store it once in `${CLAUDE_PLUGIN_ROOT}/checklists/<name>.md` and reference the file from each call site. Consumers (audit-skill, conditional reviewers) read the checklist when scoring. The runtime-efficiency anti-pattern list (`checklists/runtime-efficiency.md`) is the first instance. Single source of truth; the checklist updates independently of every call site.
