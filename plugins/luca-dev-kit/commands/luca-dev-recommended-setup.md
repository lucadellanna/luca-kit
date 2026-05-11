---
description: One-time dev environment setup for luca-dev-kit. Run once after installing the plugin in a persistent local checkout.
---

# luca-dev-kit Recommended Setup

Run this once per machine after installing luca-dev-kit. Not needed in Conductor workspaces (ephemeral environments).

## Step 1: Check if already run

```bash
if test -f "$(git rev-parse --show-toplevel)/.git/.luca-dev-kit-setup"; then echo exists; else echo missing; fi
```

If `exists`: tell the user setup was already completed and ask whether to re-run or skip. If skip, stop.

## Step 2: Install pre-commit hooks

Invoke `luca-dev-kit:install-pre-commit-hooks`.

This installs a git hook that checks for em-dashes, potential secrets (via gitleaks if installed), and type errors before every `git commit` in this repo.

## Step 3: Gemini Code Assist notice

Inform the user:

> **Note:** `/open-pr` hands off to `/review-loop`, which requires the **Gemini Code Assist GitHub App** to be installed on the repository. Without it, review-loop will stall waiting for Gemini review comments that never arrive.
>
> Install it at: `https://github.com/<owner>/<repo>/settings/installations`

## Step 4: Write marker and summarize

```bash
touch "$(git rev-parse --show-toplevel)/.git/.luca-dev-kit-setup"
```

Tell the user what was done and that setup only needs to run once per machine.
