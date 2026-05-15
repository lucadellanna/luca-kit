import json
import os

path = os.path.expanduser("~/.claude.json")
try:
    with open(path) as f:
        cfg = json.load(f)
    qmd_cfg = cfg.get("mcpServers", {}).get("qmd", {})
    cmd = qmd_cfg.get("command", "")
    if os.path.isfile(cmd) and os.access(cmd, os.X_OK):
        print("already_registered")
    else:
        print("need_to_register")
except (FileNotFoundError, json.JSONDecodeError, AttributeError):
    print("need_to_register")
