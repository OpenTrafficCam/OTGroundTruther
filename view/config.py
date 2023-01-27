import platform

OS: str = platform.system()
"""OS OTGroundTruther is currently running on"""

ON_WINDOWS: bool = OS == "Windows"
"""Wether OS is Windows or not"""

ON_LINUX: bool = OS == "Linux"
"""Wether OS is Linux or not"""

ON_MAC: bool = OS == "Darwin"
"""Wether OS is MacOS or not"""

LEFT_CLICK_EVENT: str = "<Button-1>"
LEFT_CLICK_EVENT_NUMBER: int = 1

RETURN_KEYBIND_IS_ENABLED = False

if ON_WINDOWS:
    RIGHT_CLICK_EVENT: str = "<Button-3>"
    MIDDLE_CLICK_EVENT: str = "<Button-2>"
    RIGHT_CLICK_EVENT_NUMBER: int = 3

elif ON_MAC:
    RIGHT_CLICK_EVENT: str = "<Button-2>"
    MIDDLE_CLICK_EVENT: str = "<Button-3>"
    RIGHT_CLICK_EVENT_NUMBER: str = 2
else:
    RIGHT_CLICK_EVENT: str = "<Button-3>"
    MIDDLE_CLICK_EVENT: str = "<Button-2>"
    RIGHT_CLICK_EVENT_NUMBER: int = 3
