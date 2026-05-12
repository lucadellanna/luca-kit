---
name: install-pre-commit-hooks
description: One-time installer of luca-dev-kit's git pre-commit hook (em-dash, secrets, typecheck). Invoked automatically by open-pr on first run. Safe to run manually.
version: 0.1.0
---

# Install Pre-Commit Hooks

Installs the luca-dev-kit pre-commit hook into the current repo's `.git/hooks/`. Idempotent.

## Step 1: Check if already installed

```bash
grep -q "luca-dev-kit" "$(git rev-parse --git-common-dir)/hooks/pre-commit" 2>/dev/null \
  && echo "installed" || echo "not-installed"
```

If `installed`: report "Pre-commit hook already installed." and stop.

## Step 2: Detect existing hook manager

Check for framework-managed hooks: these have their own config files and will overwrite a manually placed hook:

```bash
REPO_ROOT=$(git rev-parse --show-toplevel)
GIT_HOOKS=$(git rev-parse --git-common-dir)/hooks

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
> "This repo uses Husky. To add luca-dev-kit checks, add this to `.husky/pre-commit`:
> `source <PLUGIN_DIR>/scripts/pre-commit`
> Shall I add it? (yes/no)"
If yes: append the line (with newline guard). Stop: do not touch `.git/hooks/`.

**If PRE_COMMIT_FRAMEWORK:** Tell the user:
> "This repo uses the pre-commit framework (`.pre-commit-config.yaml`). luca-dev-kit's checks cannot be added as a local hook automatically. Add them manually or run `luca-dev-kit:install-pre-commit-hooks` in a repo without the pre-commit framework."
Stop.

**If LEFTHOOK:** Same message as PRE_COMMIT_FRAMEWORK, naming lefthook. Stop.

**If NONE:** Continue to step 3.

## Step 3: Check for existing bare hook

```bash
[[ -f "$GIT_HOOKS/pre-commit" ]] && echo "exists" || echo "none"
```

If `exists` and does NOT contain `luca-dev-kit`:
- Back up first: `cp "$GIT_HOOKS/pre-commit" "$GIT_HOOKS/pre-commit.bak.$(date +%s)"`
- Tell user: "Found existing pre-commit hook: backed up to `pre-commit.bak.<ts>`. I will append luca-dev-kit checks to it."
- Mode: append (step 5b).

If `none`: mode is fresh-write (step 5a).

## Step 4: Ask permission and configure preferences

Ask two questions. Ask them together in one message:

> "May I install a pre-commit hook with the following checks?
>
> Always on:
> - Em-dash check (blocks commits containing :)
> - gitleaks secrets scan (if gitleaks is installed)
>
> Optional:
> - Typecheck (tsc / vue-tsc / pyright): catches type errors on each commit, but may slow commits if your project is large.
>
> 1. Install the hook? (yes/no)
> 2. Enable typecheck? (yes/no)"

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

If no preference file exists when the hook later runs, typecheck is skipped with a note to re-run `install-pre-commit-hooks` to configure it.

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
  echo "❌ Hook write failed: luca-dev-kit marker not found after install." >&2; exit 1
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

Report:
- Hook installed at `<path>`
- Whether fresh write or appended, and whether a backup was made
- Whether `.gitignore` was updated
- "The hook will run on every `git commit` in this repo."
