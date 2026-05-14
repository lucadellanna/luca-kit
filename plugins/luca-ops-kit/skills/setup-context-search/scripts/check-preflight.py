import json
import os

path = os.path.expanduser("~/.claude.json")
try:
    with open(path) as f:
        cfg = json.load(f)
    qmd_cfg = cfg.get("mcpServers", {}).get("qmd", {})
    cmd = qmd_cfg.get("command", "")
    if os.path.isfile(cmd) and os.access(cmd, os.X_OK):
        print("qmd_configured")
    elif qmd_cfg:
        print("qmd_registered_broken")
    else:
        print("qmd_not_configured")
except (FileNotFoundError, json.JSONDecodeError, AttributeError):
    print("qmd_not_configured")
