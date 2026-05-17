# This repo contains four plugins

| Plugin | Path | Audience | Purpose |
|---|---|---|---|
| `luca-ops-kit` | `plugins/luca-ops-kit/` | Non-technical business users | Meta-skills for turning SOPs and procedures into reusable Claude workflows |
| `luca-dev-kit` | `plugins/luca-dev-kit/` | Developers | Pre-PR quality gates, autonomous Gemini review loop, pre-commit hook management |
| `luca-reflection-kit` | `plugins/luca-reflection-kit/` | All Claude Code users | Self-reflection and cross-session learning: reflect, dream, and optimization-hint / workflow-hint hooks |
| `luca-kit` | `plugins/luca-kit/` | All Claude Code users | Distributable plugin: simplified reflect skill and productivity hooks |

Runtime instructions for each plugin ship in their own `plugins/<name>/CLAUDE.md`. Root `CLAUDE.md` is developer-only.

---

# luca-ops-kit

Meta-workflow toolkit that helps non-technical organizations turn recurring tasks, SOPs, wiki pages, and managerial know-how into reusable Claude Skills. Ships structured workflows for building skills, auditing them, extracting procedures, creating company context, and setting explicit success criteria, red flags, human approval points, and decision boundaries. Domain skills (the actual business procedures) are added by holding companies on top of this base layer.

**Layer model:**
- **luca-ops-kit (this plugin):** meta-skills only: the toolkit for building and improving procedures
- **Holdco layer:** domain skills curated for a specific industry or portfolio (holding companies, investors, franchisors, trade associations, operating groups)
- **Partner company:** uses both layers; adapts holdco domain skills to their local context


**Skill category constraint:** All skills are meta-skills. When adding a skill, confirm it fits the meta layer: build, govern, or improve procedures; never encode a specific business procedure.

## Structure

```
plugins/luca-ops-kit/
  .claude-plugin/plugin.json     # Plugin manifest
  CLAUDE.md                      # Runtime instructions (ships with plugin)
  commands/<name>.md             # Slash commands (explicit user-triggered actions)
  skills/<name>/SKILL.md         # Skills (loaded on every execution)
  skills/<name>/DESIGN.md        # Design decisions (loaded only during audits)
  skills/<name>/REQUIREMENTS.md  # Quality contract (loaded by audit-skill)
  skills/<name>/HELP.md          # One-paragraph user-facing description (read by /help)
  design/<name>.md               # Design decisions for commands
  checklists/<name>.md           # Cross-cutting rules referenced from multiple skills
  hooks/hooks.json               # Plugin-level hooks (auto-installed)
  hooks/<name>.sh                # Bash hook scripts
  hooks/<name>.py                # Python hook scripts
```

Skill directories use kebab-case verb-noun names (e.g., `review-invoice`, `onboard-client`). Command files use kebab-case names (e.g., `undo-setup.md`).

**Auto-discovery:** Commands and skills are discovered by convention, not registered in `plugin.json`; both are invocable as `/<plugin>:<name>`. Command name is filename without `.md`; skill name is the `name` field in SKILL.md frontmatter (falls back to directory name).

**All new skills must be created via `/create-skill`.** Never write SKILL.md files directly. The guided workflow ensures quality gates (elicitation, scoring, code review, audit) are applied consistently.

**Commands vs skills:** Commands are explicit user-triggered actions (setup, teardown, one-shot operations). Skills are capabilities Claude applies as part of a workflow. If it should only fire when the user types `/name`, it's a command.

**Plugin artifacts live in the plugin tree.** When working inside this repo, all plugin artifacts (hooks, hook scripts, skills, commands, design docs) must live under `plugins/<name>/` and be registered via the plugin's manifest. Never install plugin-domain artifacts in the user's global `~/.claude/`. If an artifact is genuinely user-personal (not part of any plugin), justify why explicitly before placing it globally.

**`plugins/luca-ops-kit/CLAUDE.md` is the plugin runtime manifest.** It ships with the plugin and is loaded on every session where the plugin is active. The root `CLAUDE.md` (this file) is developer-only and never reaches user machines. Anything Claude must know to execute the plugin's skills on a user's machine (audience context, runtime principles, inter-skill data contracts) belongs there; authoring patterns, project structure notes, and quality gates stay here.

## Task tracking

In this repo, use TaskCreate/TaskUpdate/TaskList for any 3+ action sequence (skill authoring, audits, reviews). Mark `in_progress` at start and `completed` at finish; do not batch completions.

## Inter-skill patterns (authoring)

- **Complex skill review.** Before writing a complex skill (multi-step orchestration, state management, inter-skill delegation), run two independent Sonnet review passes on the plan; each reviewer starts with no conversation context, reliably surfacing issues that in-context review misses.
- **Gitignore generated state files.** When a skill generates a local state or cache file, add it to `.gitignore` immediately. The skill's note can then confirm it is already excluded rather than instructing the user to exclude it.
- **Incremental-edit Sonnet gate.** When a complex skill receives 3 or more incremental edits in one session, run one final independent Sonnet pass on the complete updated file before committing. In-context incremental review misses bugs and edge cases that accumulate across edits.
- **Pre-write review gate.** When a skill generates content that will be written to the user's system (scripts, config entries, generated files), run the code-reviewer sub-agent on the planned content before writing, not after. Apply any fixes in-context, then write the corrected version. Post-write review creates inconsistent state: the unfixed version is already on disk and registered, and rollback is unspecified.
- **Opus security gate.** Fires when implementing any feature that: (a) writes to the user's global environment (settings.json, CLAUDE.md, hook scripts, global config), (b) adds or modifies shell scripts executed in the user's environment, or (c) rewrites security-sensitive logic (input validation, secret handling, auth). Run an Opus review pass on the full plan before writing code. In-context Sonnet review is anchored to already-accepted design decisions; Opus starting fresh treats them as open questions and catches what anchored review misses. This gate precedes the inline Sonnet review.
- **Pre-push proactive scan for any .md files with embedded code.** Before the first git push on any PR that adds or modifies .md files (SKILL.md, command files, hook scripts, or any other markdown) containing Python or Bash code blocks, spawn an Opus sub-agent to review only the added/modified code blocks against ~/.claude/code-review-checklist.md. Quote offending lines and propose minimal fixes. This catches most issues in one pass instead of across multiple Gemini review rounds.
- **README row for every new artifact.** When adding a hook to hooks.json, a skill to skills/, or a command to commands/, add a corresponding row to the README.md table (## Hooks or ## Skills as appropriate) in the same commit. An artifact without a README entry is an incomplete change.
- **One-line descriptions on discovery surfaces focus on outcome, not mechanism.** When writing a one-line description for a skill, command, or hook in a discovery surface (README table, plugin CLAUDE.md table, or a skill's `description` frontmatter), lead with what the user gets, not how it works. Listing every output target ("memory, skill, CLAUDE.md, path rule") belongs in SKILL.md, not discovery surfaces.
- **Skill output is a product for the user, not a tour of how the skill is organised.** When a skill produces user-facing text, the output exists for the user to decide and act on. Hide internal categories and labels, do not narrate procedural steps the skill will take on its own, and lead with what the user gets. The skill's structure helps Claude find the right output; it should not be visible to the user.
- **Transformation-skill safety check measures IMPORTANT loss, not any change.** When a skill's purpose is to remove or transform content, the safety check (reviewer or verifier) flags only accidental loss of load-bearing info, not deliberate removals. A check that defends every word neuters the skill. Calibrate the bar to: "would a reader applying this rule make a different decision because of the change?" If no, do not flag. The claude-md-loss-verifier (`plugins/luca-kit/agents/claude-md-loss-verifier.md`) is the reference implementation.

## Setup command requirements

Skills that install third-party tools or configure the user's environment must meet the requirements in [`plugins/luca-ops-kit/checklists/setup-command-requirements.md`](plugins/luca-ops-kit/checklists/setup-command-requirements.md).

---

# luca-dev-kit

Runtime instructions: `plugins/luca-dev-kit/CLAUDE.md`.

---

# luca-reflection-kit

Runtime instructions: `plugins/luca-reflection-kit/CLAUDE.md`.