---
name: install-pre-commit-hooks
description: One-time installer of luca-dev-kit's git pre-commit hook (em-dash, secrets, typecheck). Invoked automatically by open-pr on first run. Safe to run manually.
version: 0.1.0
---

# Install Pre-Commit Hooks

Installs the luca-dev-kit pre-commit hook into the repo's hooks directory (resolved via `git rev-parse --git-path hooks`). Idempotent.

## Step 1: Check if already installed

```bash
grep -q "luca-dev-kit" "$(git rev-parse --git-path hooks/pre-commit)" 2>/dev/null \
  && echo "installed" || echo "not-installed"
```

If `installed`: report "Automatic quality checks are already set up for this project. Nothing to do." and stop.

## Step 2: Detect existing hook manager

Check for framework-managed hooks: these have their own config files and will overwrite a manually placed hook:

```bash
REPO_ROOT=$(git rev-parse --show-toplevel)
GIT_HOOKS=$(git rev-parse --git-path hooks)

if [[ -d "$REPO_ROOT/.husky" ]]; then
  echo "HUSKY"
elif [[ -f "$REPO_ROOT/.pre-commit-config.yaml" ]]; then
  echo "PRE_COMMIT_FRAMEWORK"
elif [[ -f "$REPO_ROOT/lefthook.yml" ]] || [[ -f "$REPO_ROOT/lefthook.yaml" ]]; then
  echo "LEFTHOOK"
else
  echo "NONE"
fi
```

**If HUSKY:** Tell the user:
> "This project already has an automated check system set up. I can add luca-dev-kit's quality checks to it. Shall I do that? (yes/no)"
If yes: append the line (with newline guard). Stop: do not touch `.git/hooks/`.

**If PRE_COMMIT_FRAMEWORK:** Tell the user:
> "This project uses a third-party tool to manage automated checks, and I can't add to it automatically. Please ask your developer to add luca-dev-kit's checks manually (add `source <PLUGIN_DIR>/scripts/pre-commit` to `.pre-commit-config.yaml`)."
Stop.

**If LEFTHOOK:** Tell the user:
> "This project uses a third-party tool to manage automated checks, and I can't add to it automatically. Please ask your developer to add luca-dev-kit's checks manually (add `source <PLUGIN_DIR>/scripts/pre-commit` to your lefthook config)."
Stop.

**If NONE:** Continue to step 3.

## Step 3: Check for existing bare hook

```bash
[[ -f "$GIT_HOOKS/pre-commit" ]] && echo "exists" || echo "none"
```

If `exists` and does NOT contain `luca-dev-kit`:
- Back up first: `cp "$GIT_HOOKS/pre-commit" "$GIT_HOOKS/pre-commit.bak.$(date +%s)"`
- Tell user: "This project already has some automated checks set up. I've saved a backup and will add luca-dev-kit's checks alongside them."
- Mode: append (step 5b).

If `none`: mode is fresh-write (step 5a).

## Step 4: Ask permission and configure preferences

Ask two questions. Ask them together in one message:

> "I'd like to set up automatic quality checks that run every time someone saves code to this project. Here's what they do:
>
> Always included:
> - Catches a specific dash character (the em dash) that causes problems in Claude's written output
> - Scans for accidentally included passwords or API keys (only runs if your team has this scanning tool installed)
>
> Optional:
> - Code error check: scans for mistakes in the code before it's saved. Helpful, but can slow things down in very large projects.
>
> 1. Set up these automatic checks? (yes/no)
> 2. Include the code error check? (yes/no)"

If answer to (1) is no: stop without writing anything.

Store typecheck preference (regardless of answer to (1) so it can be used as a default if re-run):
```bash
mkdir -p "$REPO_ROOT/.claude/cache"
TYPECHECK_ENABLED=<true or false based on answer to (2)>
TYPECHECK_ENABLED="$TYPECHECK_ENABLED" python3 -c "
import json, os
prefs = {'typecheck': os.environ['TYPECHECK_ENABLED'] == 'true'}
tmp = '.claude/cache/pre-commit-prefs.json.tmp'
with open(tmp, 'w') as f:
    json.dump(prefs, f)
os.replace(tmp, '.claude/cache/pre-commit-prefs.json')
"
```

If no preference file exists when the hook later runs, typecheck is skipped with a note: "Code error check not configured. Run luca-dev-kit:install-pre-commit-hooks to set it up."

## Step 5: Install hook

`PLUGIN_DIR` is the root of the luca-dev-kit plugin. Locate it via `$CLAUDE_PLUGIN_ROOT` if set, or as the directory three levels above this SKILL.md (`skills/install-pre-commit-hooks/SKILL.md` → plugin root). Fail loudly if the path cannot be resolved.

Verify `$PLUGIN_DIR/scripts/pre-commit` exists before proceeding. If it does not, stop with an error.

**5a: Fresh write:**
```bash
cp "$PLUGIN_DIR/scripts/pre-commit" "$GIT_HOOKS/pre-commit"
chmod +x "$GIT_HOOKS/pre-commit"
```

**5b: Append to existing hook:**
```bash
# Ensure file ends with a newline before appending
GIT_HOOKS="$GIT_HOOKS" python3 -c "
import os
p = os.path.join(os.environ['GIT_HOOKS'], 'pre-commit')
with open(p, 'rb+') as f:
    f.seek(0, 2)
    if f.tell() > 0:
        f.seek(-1, 2)
        if f.read(1) != b'\n':
            f.write(b'\n')
"
cat >> "$GIT_HOOKS/pre-commit" << HOOKEOF

# ── luca-dev-kit checks ──────────────────────────────────────────────────────
source "$PLUGIN_DIR/scripts/pre-commit"
HOOKEOF
```

After writing, verify the hook contains `luca-dev-kit` (sanity check):
```bash
grep -q "luca-dev-kit" "$GIT_HOOKS/pre-commit" || {
  echo "❌ Setup failed: the quality check file was not written correctly. Try running the setup again." >&2; exit 1
}
```

## Step 6: Ensure `.claude/cache/` is gitignored

```bash
GITIGNORE="$REPO_ROOT/.gitignore"
if ! grep -qE '^\.claude/cache/' "$GITIGNORE" 2>/dev/null; then
  # Ensure file ends with newline before appending
  GITIGNORE="$GITIGNORE" python3 -c "
import os
p = os.environ['GITIGNORE']
if os.path.exists(p):
    with open(p, 'rb+') as f:
        f.seek(0, 2)
        if f.tell() > 0:
            f.seek(-1, 2)
            if f.read(1) != b'\n':
                f.write(b'\n')
"
  printf '.claude/cache/\n' >> "$GITIGNORE"
fi
```

## Step 7: Confirm

Report in plain language:
- "Automatic quality checks are now set up for this project. They'll run every time someone saves new code."
- If a backup was made: "Your existing checks were preserved; I saved a backup just in case."
- If typecheck was enabled: "The code error check is included."
- If typecheck was skipped: "The code error check was not included. You can add it later by re-running this setup."
- Do not mention file paths, `.gitignore`, or technical implementation details.
