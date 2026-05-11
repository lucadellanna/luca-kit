# luca-ops-kit project memory

## Workflow patterns

**PreToolUse hook + compound git commands**: `git add && git commit` fails to stage when the hook fires on the full command string before any part runs. Always stage in a separate Bash call, verify clean, then commit.

**--no-verify scope**: `--no-verify` bypasses `.git/hooks/` scripts only. Claude Code PreToolUse hooks fire before the Bash tool executes and cannot be bypassed with `--no-verify`. Fix the underlying content instead.

**Project MEMORY.md format**: `.claude/memory/MEMORY.md` uses inline bold one-liners only. Separate files with frontmatter (`---\nname: ...\n---`) belong in global `~/.claude/MEMORY.md`, not in the project memory directory.

**AskUserQuestion option limit**: max 4 options per question. Split into multiple questions when presenting more than 4 choices.

**Bulk text substitution**: for find-and-replace with known search strings (e.g., em dash fixes), use a single Python script that opens/replaces/writes files directly from disk; no `Read` calls. `Read` loads content into context; Python `str.replace()` doesn't. Pattern: (1) one scan to identify occurrences, (2) one script fixing all files, (3) one verification scan.

**Subagent delegation threshold**: delegate file read+analyze+write tasks to a subagent when (a) the file content you'd load into context exceeds the subagent spawn overhead, or (b) the semantic analysis is complex enough to benefit from a dedicated reasoning pass. Below that bar — short files, simple substring checks — do it entirely in an inline Python script that never loads content into context.

**Git commit with env-var prefix**: use `python3 -c "open('/tmp/msg.txt','w').write(msg)"` + `git commit -F /tmp/msg.txt` instead of heredocs when `SPECS_REVIEWED=1` or similar env-var prefixes are needed; shell metacharacter expansion breaks `$(cat <<'EOF'...)` syntax.

**Subagents: pass paths not content**: pass file paths to subagents; let them read with their own tools. Exception: filtering or transformation needed before the subagent sees the content.

**Subagent review prompts**: always include "quote the exact lines you are flagging" : prevents hallucinated findings that cite non-existent or misread content.

## Design patterns

**Raw-mode inter-skill data contract**: any skill that produces data another skill may consume must support `mode: raw` in the opening message: return structured TSV/JSON output, skip rendering. Never embed another skill's script inline; invoke in raw mode instead. Established in `list-skills` v0.2.

## Setup skill patterns

**pnpm v10+ blocks native module builds.** pnpm v10+ silently skips native build scripts (`better-sqlite3`, `node-llama-cpp`, etc.) by default for security. The only fix is `pnpm approve-builds -g`, which is an interactive terminal menu that can't be automated. For any setup skill installing npm packages with native modules: default to npm, warn before pnpm, and verify the binary functionally (not just `--version`) after install.

**Always `os.makedirs` before writing to `~/.claude/` paths.** On fresh installs, `~/.claude/` may not exist. Any Python code that opens files or lock files in that directory must call `os.makedirs(os.path.dirname(path), exist_ok=True)` first, or the skill fails on first-time users.

## Plugin development

**Cache vs workspace layering**: when developing luca-ops-kit in a Conductor workspace while the plugin is also installed, skill invocations (e.g. `/luca-ops-kit:reflect`) run from `~/.claude/plugins/cache/`, not the workspace. Workspace edits are invisible to running skills until the plugin is republished and reinstalled.

**Version bump rule**: bump the SKILL.md frontmatter version after every meaningful change: patch (0.x.y → 0.x.y+1) for fixes or additions to existing steps; minor (0.x.0 → 0.x+1.0) for new steps added. The version field is what the Claude plugin system uses to signal an update to cached users.
