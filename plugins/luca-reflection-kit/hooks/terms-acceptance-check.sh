#!/bin/bash
# luca-reflection-kit:terms-acceptance-check:v1
# Fires on SessionStart. Silent in non-interactive contexts and once the user
# has acknowledged on this Claude install.
set -u

# Non-interactive guard: skip when stdin is not a TTY (claude -p, agent SDK,
# cron, CI). Injecting a nag into automation context is noise the user can
# neither see nor act on.
if [ ! -t 0 ]; then
  exit 0
fi

MARKER="${HOME}/.claude/luca-ops-kit/terms-accepted-v1.json"
if [ -f "${MARKER}" ]; then
  exit 0
fi

# Output is injected into Claude's SessionStart context. Address Claude
# (not the user) so Claude translates the instruction to the user's level.
# IMPORTANT: this is an informational nudge, not a trigger. Claude must
# NOT invoke /luca-reflection-kit:accept-terms itself; the user has to
# choose to run it. Auto-invocation would coerce the acknowledgment.
echo "The user has not yet reviewed the interim notice for Luca's plugins on this Claude install. On your first response, tell the user (in plain language) that they should run the /luca-reflection-kit:accept-terms command when convenient, and briefly explain how to invoke a slash command (type / and pick from the menu, or type the full /luca-reflection-kit:accept-terms). One-time. Stored locally; no server calls. Do NOT invoke /luca-reflection-kit:accept-terms yourself; the user must run it of their own choice. Do not show this reminder more than once per session."
exit 0
