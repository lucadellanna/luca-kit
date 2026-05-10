# luca-dev-kit

Runtime instructions active in every session where this plugin is installed.

## First-run

**Disclaimer (once per install):** If `~/.claude/luca-dev-kit/disclaimer-v1.0-shown` does not exist:
1. Run `cat "$CLAUDE_PLUGIN_ROOT/DISCLAIMER.md"` and display the output verbatim.
2. Run `mkdir -p ~/.claude/luca-dev-kit && echo "v1.0 shown $(date +%Y-%m-%d)" > ~/.claude/luca-dev-kit/disclaimer-v1.0-shown`
3. Do not display it again this session.

## What this plugin does

| Skill | Trigger | Purpose |
|---|---|---|
| `luca-dev-kit:open-pr` | "open pr", "create pr", "/open-pr" | Pre-PR quality gates + PR creation + hands off to review-loop |
| `luca-dev-kit:review-loop` | Auto-invoked by open-pr, or "review loop", "/review-loop" | Autonomous Gemini fix loop: no user input after start |
| `luca-dev-kit:triple-review` | "triple review", or invoked by open-pr | Three-lens parallel code review (standalone or as part of open-pr) |
| `luca-dev-kit:specs-adherence-review` | "check specs", "adheres to principles?", or invoked as Lens A | Principles check vs ~/.claude/CLAUDE.md + local CLAUDE.md/AGENTS.md |
| `luca-dev-kit:install-pre-commit-hooks` | Invoked by open-pr on first run | One-time git hook installer |

## Principles

- **Autopilot by default.** After `open-pr` is invoked, no user input is needed until review-loop exits or a stop condition fires.
- **Stop conditions are explicit.** Any stop must report: what stopped, why, and what the user must do next. Never exit silently.
- **Delegation over reimplementation.** When a global skill exists (`commit-commands:commit`), invoke it rather than reimplementing its logic.
- **Time-budget gates.** Pre-commit hooks skip slow checks in future commits once a timing threshold is exceeded; `open-pr` always runs them regardless.
- **No assumptions about project type.** Detect build tools and type checkers from repo files. Skip gracefully if not found.
- **Self-observation.** During skill execution, log problems encountered (unexpected behavior, missed authoring gates, tool failures, wasted iterations) to a running task list. After the main work completes, investigate each item for root cause and decide whether a permanent fix is needed (skill edit, CLAUDE.md rule). Apply fixes before closing the task.

## Code review checklist

`review-loop` reads from `~/.claude/code-review-checklist.md` (Lens B). This is a personal, per-user corpus that accumulates over time as Gemini flags new bug classes. It is not shipped with the plugin. If the file does not exist, `review-loop` creates it empty on first use. Format: one line per pattern, `- <what to check>: <why it matters>`.

