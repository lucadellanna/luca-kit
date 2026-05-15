---
description: Configure session notes for /reflect. Decides once whether to save private session logs to your computer. Run this after accepting the plugin terms.
---

# Luca Reflection: Recommended Setup

## Step 1: Ask about session notes

Use AskUserQuestion (singleSelect):

Question: "Can I save a private note after each /reflect session? Future sessions can then spot patterns over time. Notes stay on your computer only; nothing is sent anywhere."

Options:
- "Yes, save session notes"
- "No thanks, never ask again"
- "Skip for now (ask me next time)"

## Step 2a: "Yes, save session notes"

Run:

```bash
mkdir -p ~/.claude/reflect-logs && touch ~/.claude/reflect-logs/.enabled && rm -f ~/.claude/reflect-logs/.disabled
```

Then check for Python 3:

```bash
command -v python3 >/dev/null 2>&1 && echo "ok" || echo "missing"
```

- `ok`: tell the user: "Done. After each /reflect, I'll save a short private note. You can change this any time by running `/luca-reflection-kit:luca-reflection-recommended-setup` again."
- `missing`: tell the user: "Done, but session notes need Python 3, which doesn't seem to be installed yet. Notes will start saving once you install it. You can get it from python.org, or ask your IT team."

## Step 2b: "No thanks, never ask again"

Run:

```bash
mkdir -p ~/.claude/reflect-logs && touch ~/.claude/reflect-logs/.disabled && rm -f ~/.claude/reflect-logs/.enabled
```

Tell the user: "No problem. I won't ask again. You can change this any time by running `/luca-reflection-kit:luca-reflection-recommended-setup` again."

## Step 2c: "Skip for now"

Tell the user: "Skipped. I'll remind you once the next time /reflect runs."

## Step 3: Show skill overview

After any Step 2 outcome, show:

> **What luca-reflection-kit offers**
>
> | Skill | What it does |
> |-------|-------------|
> | `/reflect` | After a session, surfaces improvement points, auto-applies safe memory updates, and asks about anything riskier |
> | `/dream` | Mines your /reflect logs to surface cross-session patterns: recurring issues, memory contradictions, improvements that keep coming up |
> | `/setup-context-search` | *(Power users, optional)* Installs [qmd](https://github.com/tobi/qmd), a local semantic search engine. After setup, `/reflect` and `/dream` detect conceptual overlaps in your knowledge base when proposing new rules or skills. Requires Node.js 22+. |
>
> Run `/luca-reflection-kit:setup-context-search` if you want to enable the semantic overlap detection.
