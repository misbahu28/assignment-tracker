import os
from pathlib import Path

DATA_DIR = Path(os.environ.get("TRACKER_HOME", Path.home() / ".assignment-tracker"))