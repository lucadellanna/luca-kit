import os
from config import MARKER_PATH

try:
    os.remove(MARKER_PATH)
except FileNotFoundError:
    pass
