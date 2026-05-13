import os
import json
from datetime import datetime
from config import MARKER_PATH, TERMS_VERSION

os.makedirs(os.path.dirname(MARKER_PATH), exist_ok=True)
payload = {"version": TERMS_VERSION, "accepted_at": datetime.now().astimezone().isoformat(timespec="seconds")}
tmp = MARKER_PATH + ".tmp"
with open(tmp, "w", encoding="utf-8") as f:
    json.dump(payload, f)
    f.flush()
    os.fsync(f.fileno())
os.replace(tmp, MARKER_PATH)
