import os, json
from datetime import datetime

# When terms change materially, bump TERMS_VERSION and update the "v1" in
# MARKER_PATH to match (major only). Old acceptances won't carry over.
TERMS_VERSION = "1.0"
MARKER_PATH = os.path.expanduser("~/.claude/luca-ops-kit/terms-accepted-v1.json")

os.makedirs(os.path.dirname(MARKER_PATH), exist_ok=True)
payload = {"version": TERMS_VERSION, "accepted_at": datetime.now().astimezone().isoformat(timespec="seconds")}
tmp = MARKER_PATH + ".tmp"
with open(tmp, "w", encoding="utf-8") as f:
    json.dump(payload, f)
    f.flush()
    os.fsync(f.fileno())
os.replace(tmp, MARKER_PATH)
