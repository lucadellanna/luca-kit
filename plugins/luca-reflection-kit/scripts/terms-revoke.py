import os
from config import MARKER_PATH

if os.path.exists(MARKER_PATH):
    os.remove(MARKER_PATH)
