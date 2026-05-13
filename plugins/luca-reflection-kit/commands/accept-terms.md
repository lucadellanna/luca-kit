---
description: Review the interim notice for Luca's plugins and record your decision on this Claude install. One-time. Stored locally; no server calls.
---

## Step 0: Pre-flight check

Run via Bash: `command -v python3 >/dev/null 2>&1 && echo "ok" || echo "missing"`

If the output is `"missing"`, tell the user:

> "This command needs Python 3 to save your decision, and it doesn't seem to be installed on your machine. You can get it from python.org, or ask your IT team. Once it's installed, run `/luca-reflection-kit:accept-terms` again."

Then stop. Do not continue to the notice or question.

## Step 1: Show the interim notice verbatim

Print exactly (no paraphrasing, no translation, no extra explanation):

> **About these plugins: interim notice**
>
> These plugins are free tools made by an independent author. They work well in normal use, but the author can't promise they'll be bug-free or a fit for every situation, and can't take responsibility if something goes wrong while you use them. A clearer, fuller version of this notice will be published in a future update and will replace this one.
>
> Your choice is saved on this computer. Nothing is sent to any server.

**Notes for Claude (not part of the printed notice):**
- Print the block verbatim. Do not add section numbers, file paths, license-type names, or JSON details. Do not paraphrase or translate.
- If the user explicitly asks where the file is saved, you may tell them, but not unprompted.

## Step 2: Ask explicitly

Use AskUserQuestion (singleSelect):
- Question: `"Are you OK with this?"`
- Options: `"Yes, I understand"`, `"Not right now"`

(The "Other" option is added automatically by the tool; do not include it.)

## Step 3a: On "Yes, I understand"

Run via Bash:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/terms-accept.py"
```

Then tell the user (verbatim): `"Saved. You won't see this reminder again on this computer."`

Then add: "Tip: run `/luca-reflection-kit:luca-reflection-recommended-setup` to configure session notes for /reflect."

## Step 3b: On "Not right now"

Run via Bash:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/terms-revoke.py"
```

Then tell the user (verbatim): `"No problem. You can run this again any time."`

## Step 4: On any error in steps 3a or 3b

Surface the exact error message. Do not claim success. Tell the user nothing was saved and they should try again or report the issue.
