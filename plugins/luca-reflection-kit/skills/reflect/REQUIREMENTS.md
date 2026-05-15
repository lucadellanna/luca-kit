# Requirements

## Scope and trigger

1. Runs only on explicit user invocation ("reflect", "/reflect", "let's reflect").
2. Analyzes the conversation since the last `/reflect` in this session (or since session start if none).
3. If neither agent finds anything actionable, outputs one line saying so and stops.

## Inputs to agents

4. **Conversation digest**: verbatim user and Claude turns. Tool outputs are truncated (first 5 + last 5 lines).
5. **Rule corpus**: full text of project `MEMORY.md`, project `CLAUDE.md`, global `~/.claude/CLAUDE.md`, and plugin runtime `CLAUDE.md`, passed in-prompt.
6. **Skills + commands index**: name + one-line description of every available skill, command, and hook (project, global, all installed plugins).

## Agents

7. **Agent 1 (behavior-asset reviewer)** proposes changes to files that shape Claude's future behavior: project `MEMORY.md`, any `CLAUDE.md`, skill files, hook scripts, new skills.
8. **Agent 2 (user-hint reviewer)** proposes forward-looking suggestions for the user. Output is displayed text; nothing it produces is written to disk by the orchestrator.
9. Non-overlap is enforced by output target: Agent 1 writes files, Agent 2 displays text. A finding with a write target belongs to Agent 1 regardless of how it is phrased.
10. Each agent enumerates the categories of finding it can return; "find improvements" alone is too vague.
11. Both agents have `tools: []`. The orchestrator does all file I/O.

## Per-finding shape

12. Agent 1 returns: `target` (file path), `proposed_change` (exact text or edit), `evidence` (verbatim quote from the digest).
13. Agent 2 returns: `recommendation` (plain-language sentence), `rationale` (plain-language sentence).
14. No agent assigns risk or confidence. The orchestrator derives risk from the target.

## Triage

15. The orchestrator assigns `risk` from the target file:

| Target | Risk |
|---|---|
| Project `.claude/memory/MEMORY.md` or global `~/.claude/MEMORY.md` | safe |
| Any `CLAUDE.md` (project, global, plugin runtime) | ambiguous |
| Any existing skill file | ambiguous |
| New skill creation | ambiguous |
| Hook script (`.sh`, `.py` under `hooks/`) | security-sensitive |
| Anything else | breaking |

16. `risk = safe` → auto-apply silently, after a literal `grep -F` duplicate check against the target.
17. `risk = ambiguous | breaking | security-sensitive` → ask the user via a single `AskUserQuestion` call (cap 4 options; overflow goes to "logged only").
18. Before any write, the orchestrator runs `grep -F` on the proposed text against the target. Literal duplicates are skipped and noted, never re-written.

## Output to the user

19. One short report. Omit any empty section.
    - **Applied**: one line per auto-applied change, with file path.
    - **Hints**: Agent 2 output, max 3.
    - **Logged only**: anything that did not qualify and was not asked.
    - `AskUserQuestion` is handled inline, not in a separate rendered section.
20. No grading, no congratulations, no narrative summary of the session.
21. Plain language throughout.

## Failure modes

22. Both agents return nothing → "Nothing worth surfacing", stop after logging.
23. One agent returns nothing → proceed with the other; one-line note that the other was empty.
24. A write fails after triage → surface the failure in the report; never silently swallow.

## Idempotence

25. Two consecutive `/reflect` runs with no new conversation in between produce no new applied changes (covered by #3).
26. Literal duplicates against the target file are no-ops (#18). Semantic duplicates may slip through; cleanup belongs to `/dream`.

## Logging

27. One JSONL line per session in `~/.claude/reflect-logs/<project-slug>.jsonl`, fields: `date`, `applied[]`, `asked_accepted[]`, `asked_rejected[]`, `hints[]`. Each entry includes `target` and a short text where applicable.
28. `/reflect` does no cross-session analysis. That is `/dream`'s job.
29. Logging is gated by `~/.claude/reflect-logs/.enabled`. Silent skip if absent.

## Non-goals

30. Not a retrospective. Output is forward-looking, not a session summary.
31. No measurement of whether past rules worked (no telemetry available).
32. No file-level provenance markers; the session log is the single source of truth.

---

# Scoring criteria

Each criterion is scored 0 to 10. Target average ≥ 9.5. Below threshold, revise and re-score; cap at 3 iterations.

## Conciseness

Every step, sentence, and field earns its place. Removing it would change a behavior or lose information that is not derivable from another section. No restatement of the same rule in two places.

- 10 : every element is load-bearing; no candidate for deletion remains.
- 7 : one or two elements could be removed or merged without behavior change.
- 4 : visible duplication across sections, or steps that exist only for emphasis.
- 0 : the file is largely redundant.

## Runtime efficiency

The skill's execution path is the minimum needed to produce the required output. No agent runs that could be skipped given empty inputs. No tokens spent on data an agent does not use. Tool outputs in the digest are truncated. File reads happen once and are cached in working memory across steps.

- 10 : every agent call, file read, and prompt section is necessary for the produced output.
- 7 : one redundant read or one unused prompt section.
- 4 : agents receive data they do not use, or files are read more than once.
- 0 : the skill is wasteful in multiple places.

## Adherence to requirements

Every requirement above is implemented exactly. No requirement is silently skipped, partially implemented, or extended beyond what the requirements specify.

- 10 : every requirement is implemented as written; no scope creep, no omissions.
- 7 : one or two minor deviations with no behavioral impact.
- 4 : one substantive requirement skipped or one substantive behavior added that is not in the requirements.
- 0 : multiple requirements unmet or contradicted.
