# Hook implementation patterns

Learnings accumulated across plugin development in this repo. Update when a new pattern is confirmed or a known-bad pattern is discovered.

---

## SessionStart: detecting non-interactive contexts

**Problem:** `[ ! -t 0 ]` (stdin TTY check) does not work in hooks. Hook scripts receive the event payload as JSON on stdin -- a pipe -- so stdin is never a TTY, even in fully interactive sessions. Using this check silences the hook everywhere.

**Correct pattern:**

```bash
# 1. Remote/headless context: agent SDK, automated invocations.
# CLAUDE_CODE_REMOTE is set by Claude Code when running outside a local terminal.
if [ -n "${CLAUDE_CODE_REMOTE:-}" ]; then
  exit 0
fi

# 2. No controlling terminal: CI containers, Docker without -t, daemon processes.
# /dev/tty is the process's controlling terminal -- present in interactive
# sessions regardless of stdin redirection.
if ! { : < /dev/tty; } 2>/dev/null; then
  exit 0
fi
```

**Why two checks:** `$CLAUDE_CODE_REMOTE` covers the agent SDK and remote invocations that may still have a controlling terminal (e.g., SSH sessions with TTY). `/dev/tty` covers CI and headless environments where the process has no controlling terminal at all.

**UserPromptSubmit hooks do not need this guard.** That event fires only when a human types a prompt.

---

## SessionStart: hook input payload

The hook receives JSON on stdin with these fields (no `source` or `is_interactive` field exists):

```json
{
  "session_id": "...",
  "transcript_path": "/path/to/transcript.txt",
  "cwd": "/current/working/dir",
  "permission_mode": "ask|allow",
  "hook_event_name": "SessionStart"
}
```

Available environment variables in all command hooks: `$CLAUDE_PROJECT_DIR`, `$CLAUDE_PLUGIN_ROOT`, `$CLAUDE_CODE_REMOTE`.
SessionStart-only: `$CLAUDE_ENV_FILE` (write `export VAR=value` lines here to persist env vars into the session).

---

## Python scripts called from hooks: shared constants

When two sibling scripts share a constant (e.g., a marker file path), put it in a `config.py` in the same directory. Python adds the invoking script's directory to `sys.path` at runtime, so `from config import CONSTANT` resolves without any `sys.path` manipulation or package setup.

**Example (`scripts/config.py`):**
```python
import os

TERMS_VERSION = "1.0"
MARKER_PATH = os.path.expanduser("~/.claude/luca-ops-kit/terms-accepted-v1.json")
```

**Importing script:**
```python
from config import MARKER_PATH, TERMS_VERSION
```

This works when invoked as `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/terms-accept.py"`.

---

## Step 0: binary pre-flight in commands

Any slash command that shells out to an external binary (python3, node, etc.) must verify the binary exists before showing the user any UI:

```bash
command -v python3 >/dev/null 2>&1 && echo "ok" || echo "missing"
```

If the output is `"missing"`, surface a plain-language "not installed" message and stop. Do not continue to notices or prompts -- a failed Step 3 after the user has already responded to a prompt is confusing and wastes their time.
