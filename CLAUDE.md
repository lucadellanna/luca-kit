# luca-ops-kit

Meta-workflow toolkit that helps non-technical organizations turn recurring tasks, SOPs, wiki pages, and managerial know-how into reusable Claude Skills. Ships structured workflows for building skills, auditing them, extracting procedures, creating company context, and setting explicit success criteria, red flags, human approval points, and decision boundaries. Domain skills (the actual business procedures) are added by holding companies on top of this base layer.

**Layer model:**
- **luca-ops-kit (this plugin):** meta-skills only: the toolkit for building and improving procedures
- **Holdco layer:** domain skills curated for a specific industry or portfolio (holding companies, investors, franchisors, trade associations, operating groups)
- **Partner company:** uses both layers; adapts holdco domain skills to their local context

**Runtime instructions** (audience, principles, inter-skill runtime patterns) are in `plugins/luca-ops-kit/CLAUDE.md` -- that file is the authoritative source and ships with the plugin.

## Skill categories

All skills in this plugin are meta-skills. When adding a skill, confirm it fits the meta layer: build, govern, or improve procedures; never encode a specific business procedure.

## Structure

```
plugins/luca-ops-kit/
  .claude-plugin/plugin.json   # Plugin manifest
  CLAUDE.md                     # Runtime instructions (ships with plugin)
  skills/<name>/SKILL.md        # One directory per skill
```

Skill directories use kebab-case verb-noun names (e.g., `review-invoice`, `onboard-client`).

**All new skills must be created via `/create-skill`.** Never write SKILL.md files directly. The guided workflow ensures quality gates (elicitation, scoring, code review, audit) are applied consistently.

No commands, agents, or hooks yet: skills only.

**`plugins/luca-ops-kit/CLAUDE.md` is the plugin runtime manifest.** It ships with the plugin and is loaded into context on every session where the plugin is active. The root `CLAUDE.md` (this file) is developer-only and never reaches user machines. Authoring rule: anything Claude must know to execute the plugin's skills correctly on a user's machine belongs in `plugins/luca-ops-kit/CLAUDE.md`. This includes:
- **Audience and persona context** -- who the users are; tone and assumed knowledge
- **Runtime principles** -- plain language, guided workflows, human approval points, self-reflection, self-observation
- **First-run behavior** -- proactive setup suggestions and session-level suppression
- **Runtime inter-skill patterns** -- data contracts, manifest-as-source-of-truth, typed agent spawn rules

Authoring patterns, project structure notes, and quality gates (this file) stay in the root `CLAUDE.md` and are never duplicated into the plugin runtime manifest.

## Task tracking

Use the TaskCreate/TaskUpdate/TaskList tools extensively for all multi-step work in this repo. Create a task for each discrete step before starting it, mark it `in_progress` when beginning, and `completed` immediately when done. Do not batch completions. This applies to skill authoring, audits, reviews, and any sequence of 3 or more actions.

## Inter-skill patterns (authoring)

These apply when writing or editing skills, not at user runtime. They are enforced by authoring tools (`/create-skill`, `/audit-skill`) and do not need to be loaded in every user session.

- **Complex skill review.** Before writing the first line of a complex skill (multi-step orchestration, state management, inter-skill delegation), run two independent Sonnet review passes on the plan; each reviewer starts with no conversation context. This reliably surfaces issues that in-context review misses.
- **Gitignore generated state files.** When a skill generates a local state or cache file, add it to `.gitignore` immediately; do not leave it as a "you should" note in the skill doc. The skill's note can then confirm it is already excluded rather than instructing the user to exclude it.
- **Incremental-edit Sonnet gate.** When a complex skill (multi-step orchestration, state management, inter-skill delegation) receives 3 or more incremental edits in one session, run one final independent Sonnet pass on the complete updated file before committing. In-context incremental review misses step-sequence bugs and edge cases that accumulate across edits.
- **Pre-write review gate.** When a skill generates content that will be written to the user's system (scripts, config entries, generated files), run the code-reviewer sub-agent on the planned content before writing, not after. Apply any fixes in-context, then write the corrected version. Post-write review creates inconsistent state: the unfixed version is already on disk and registered, and rollback is unspecified.
- **Opus security gate for global-state features.** Before implementing any plugin feature that writes to the user's global environment (settings.json, CLAUDE.md, hook scripts, global config), run an Opus review pass on the plan with focus on security and plugin-owner liability. In-context Sonnet review is anchored to the plan's already-accepted decisions; Opus starting fresh treats them as open questions. This gate is separate from and precedes the inline Sonnet review.
- **Pre-push proactive scan for SKILL.md files with embedded code.** Before the first `git push` on any PR that modifies SKILL.md files containing Python or Bash code blocks, spawn a Sonnet subagent to scan all modified SKILL.md files against the full `~/.claude/code-review-checklist.md`. This catches most issues in one pass instead of across multiple Gemini review rounds. Run the same scan that review-loop Step 5 runs, but before pushing rather than after each Gemini round.
- **Design-decisions table when rejecting a Gemini thread.** When a Gemini review thread is rejected as a design decision (not a bug), update the `## Design decisions` table in the same commit. A documented decision prevents the same thread from being raised in subsequent review rounds.
