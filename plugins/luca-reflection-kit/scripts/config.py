import os

# When terms change materially, bump TERMS_VERSION and update the "v1" in
# MARKER_PATH to match (major only). Old acceptances won't carry over.
TERMS_VERSION = "1.0"
MARKER_PATH = os.path.expanduser("~/.claude/luca-ops-kit/terms-accepted-v1.json")
