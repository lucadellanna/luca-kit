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
PATH_CANDIDATE="$(command -v codex 2>/dev/null)"
if [[ "$PATH_CANDIDATE" == /* && -x "$PATH_CANDIDATE" ]]; then
  CODEX_BIN="$PATH_CANDIDATE"
else
  for candidate in /opt/homebrew/bin/codex /usr/local/bin/codex; do
    if [[ -x "$candidate" ]]; then CODEX_BIN="$candidate"; break; fi
  done
fi

if [[ -z "$CODEX_BIN" ]]; then
  echo missing-install
elif "$CODEX_BIN" doctor 2>&1 | grep -q "auth is configured"; then
  echo present
else
  echo missing-auth
fi
```

If `missing-install`: tell the user to install it (`npm install -g @openai/codex`) then run `codex login`, then re-run this step's check before continuing. Do not proceed to Step 4 until it prints `present`.
If `missing-auth`: tell the user Codex is installed but not authenticated; have them run `codex login`, then re-run this step's check before continuing. Do not proceed to Step 4 until it prints `present`.

## Step 4: Write marker and summarize

Only reached once Step 3 printed `present` (skip this step entirely, and do not write the marker, if the user chose to stop at Step 3 without fixing the install/auth issue).

```bash
touch "$(git rev-parse --git-dir)/.luca-dev-kit-setup"
```

Tell the user what was done and that setup only needs to run once per machine.
