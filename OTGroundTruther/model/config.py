import platform
from pathlib import Path

OTEVENTS_FILE_SUFFIX: str = ".otevents"
GROUND_TRUTH_EVENTS_FILE_SUFFIX: str = ".otgtevents"
OTANALYTICS_FILE_SUFFIX: str = ".otflow"
DEFAULT_VIDEO_FILE_SUFFIX: str = ".mp4"
DEFAULT_DETECTION_FILE_SUFFIX: str = ".otdet"

LOG_DIR = Path(".logs").absolute()
"""The log save directory."""

OS: str = platform.system()
"""OS OTAnalyitcs is currently running on"""

ON_WINDOWS: bool = OS == "Windows"
"""Wether OS is Windows or not"""

ON_LINUX: bool = OS == "Linux"
"""Wether OS is Linux or not"""

ON_MAC: bool = OS == "Darwin"
"""Wether OS is MacOS or not"""

if not (ON_LINUX or ON_WINDOWS or ON_MAC):
    raise RuntimeError("OTAnalytics is running on an unknown platform")
