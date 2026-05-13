import os

# Keep in sync with MARKER_PATH in terms-accept.py.
MARKER_PATH = os.path.expanduser("~/.claude/luca-ops-kit/terms-accepted-v1.json")

if os.path.exists(MARKER_PATH):
    os.remove(MARKER_PATH)
