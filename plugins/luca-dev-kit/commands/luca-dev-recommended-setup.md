---
description: One-time dev environment setup for luca-dev-kit. Run once after installing the plugin in a persistent local checkout.
---

# luca-dev-kit Recommended Setup

Run this once per machine after installing luca-dev-kit. Not needed in Conductor workspaces (ephemeral environments).

## Step 1: Check if already run

```bash
if test -f "$(git rev-parse --git-dir)/.luca-dev-kit-setup"; then echo exists; else echo missing; fi
```

If `exists`: tell the user setup was already completed and ask whether to re-run or skip. If skip, stop.

## Step 2: Install pre-commit hooks

Invoke `luca-dev-kit:install-pre-commit-hooks`.

This installs a git hook that checks for em-dashes, potential secrets (via gitleaks if installed), and type errors before every `git commit` in this repo.

## Step 3: Codex CLI check

`/open-pr` hands off to `/review-loop`, which requires the **Codex CLI** (`@openai/codex`) installed and authenticated locally -- no GitHub App or repo installation needed.

```bash
CODEX_BIN=""
for candidate in /opt/homebrew/bin/codex /usr/local/bin/codex "$(command -v codex 2>/dev/null)"; do
  if [[ -n "$candidate" && -x "$candidate" ]]; then CODEX_BIN="$candidate"; break; fi
done

if [[ -z "$CODEX_BIN" ]]; then
  echo missing-install
elif "$CODEX_BIN" doctor 2>&1 | grep -q "auth is configured"; then
  echo present
else
  echo missing-auth
fi
```

If `missing-install`: tell the user to install it (`npm install -g @openai/codex`) then run `codex login`.
If `missing-auth`: tell the user Codex is installed but not authenticated; run `codex login` before using `/open-pr`.

## Step 4: Write marker and summarize

```bash
touch "$(git rev-parse --git-dir)/.luca-dev-kit-setup"
```

Tell the user what was done and that setup only needs to run once per machine.
