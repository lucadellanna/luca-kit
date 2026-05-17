# luca-ops-kit project memory

## Workflow patterns

**PreToolUse hook + compound git commands**: `git add && git commit` fails to stage when the hook fires before any part runs. Always stage in a separate Bash call, verify clean, then commit.

**--no-verify scope**: `--no-verify` bypasses `.git/hooks/` scripts only, not Claude Code PreToolUse hooks. Fix the underlying content instead.

**Project MEMORY.md format**: `.claude/memory/MEMORY.md` uses inline bold one-liners only. Separate files with frontmatter (`---\nname: ...\n---`) belong in global `~/.claude/MEMORY.md`, not in the project memory directory.

**Bulk text substitution**: for find-and-replace with known search strings (e.g., em dash fixes), use a single Python script that opens/replaces/writes files directly from disk; no `Read` calls. Python `str.replace()` doesn't load content into context. Pattern: (1) one scan to identify occurrences, (2) one script fixing all files, (3) one verification scan.

**Subagent delegation threshold**: delegate file read+analyze+write tasks to a subagent when (a) file content exceeds spawn overhead, or (b) semantic analysis is complex enough to benefit from dedicated reasoning. Below that bar (short files, simple substring checks), do it entirely in an inline Python script that never loads content into context.

**Git commit with env-var prefix**: use `python3 -c "open('/tmp/msg.txt','w').write(msg)"` + `git commit -F /tmp/msg.txt` instead of heredocs when env-var prefixes are needed; shell metacharacter expansion breaks the heredoc syntax.

## Design patterns

**Raw-mode inter-skill data contract**: any skill that produces data another skill may consume must support `mode: raw` in the opening message: return structured TSV/JSON output, skip rendering. Never embed another skill's script inline; invoke in raw mode instead. Established in `list-skills` v0.2.

## Setup skill patterns

**pnpm v10+ blocks native module builds.** pnpm v10+ silently skips native build scripts (`better-sqlite3`, `node-llama-cpp`, etc.) by default for security. The only fix is `pnpm approve-builds -g`, which is an interactive terminal menu that can't be automated. For any setup skill installing npm packages with native modules: default to npm, warn before pnpm, and verify the binary functionally (not just `--version`) after install.

**Always `os.makedirs` before writing to `~/.claude/` paths.** On fresh installs, `~/.claude/` may not exist. Any Python code that opens files or lock files in that directory must call `os.makedirs(os.path.dirname(path), exist_ok=True)` first, or the skill fails on first-time users.

## luca-dev-kit authoring

**luca-dev-kit cache dir**: `.claude/cache/` is gitignored; contains `review-loop-state.json`, `pre-commit-prefs.json`, and `typecheck-timing.json`. Created by `review-loop`.

**pre-commit security gate**: `scripts/pre-commit` is installed into `.git/hooks/`; any changes must pass the Opus security gate before merging.
**code-review-checklist**: `~/.claude/code-review-checklist.md` is auto-accumulated by `review-loop`; not shipped with the plugin, created on first run.

**install-pre-commit-hooks audience**: target non-technical users who may not know git. No tool names (gitleaks, tsc, Husky), no file paths, no technical jargon in any user-facing messages. Applies to any luca-dev-kit skill invoked via `luca-dev-recommended-setup`. Use plain English: "saves code" not "commits", "automated checks" not "pre-commit hooks".

## Plugin development

**Cache vs workspace layering**: when developing luca-ops-kit in a Conductor workspace while the plugin is also installed, skill invocations (e.g. `/luca-ops-kit:reflect`) run from `~/.claude/plugins/cache/`, not the workspace. Workspace edits are invisible to running skills until the plugin is republished and reinstalled.

**Parallel Agent calls + `subagent_type`**: both are valid in Claude Code; treat reviewer claims that they are unsupported as hallucinations and verify against the tool schema, not the reviewer.

**Plugin layout decisions invoke `plugin-dev:plugin-structure`**: when deciding where files live in a plugin (agents/, commands/, skills/), invoke that skill before asserting; inferring from intra-skill patterns is unreliable.

## luca-reflection-kit artifacts

**reflect**: conversational analysis skill; no durable artifacts beyond user-approved session logs and memory writes.
**dream**: cross-session pattern mining; reads reflect logs, writes nothing without user approval.
**optimization-hint hook**: stateless UserPromptSubmit; scoped to Claude-side improvements (memory entries, edits to existing skills).
**workflow-hint hook**: stateless UserPromptSubmit; scoped to user-side automation (new skills, automating workflows, removing friction).
**terms-acceptance-check hook**: SessionStart; checks `~/.claude/luca-ops-kit/terms-accepted-v1.json`; silent when `$CLAUDE_CODE_REMOTE` set or no controlling terminal.

## luca-reflection-kit authoring

See [luca-reflection-kit-authoring-notes.md](luca-reflection-kit-authoring-notes.md) for agent tooling, mandate/output-target separation, hook minimalism, and consent hook constraints.

## CLAUDE.md authoring

**Plugin vs. skill versioning are independent**: `plugin.json` version follows semver for the plugin as a whole (patch: bug fixes; minor: new skills/agents/steps; major: breaking changes). Skill versions track individual skill changes. The two numbers do not need to match and should not be kept in sync by convention.

## Plugin runtime pointers

**luca-dev-kit**: see `plugins/luca-dev-kit/CLAUDE.md` for runtime instructions.
**luca-reflection-kit**: see `plugins/luca-reflection-kit/CLAUDE.md` for runtime instructions.
