from dataclasses import dataclass
from typing import ClassVar

from OTGroundTruther.model.config import ON_MAC

PADX = 10
PADY = 5
STICKY = "NESW"

STATE_DISABLED = "disabled"
STATE_NORMAL = "normal"

PREVIEW_IMAGE_FILE: str = r"assets/OpenTrafficCam_800.png"
JUMP_TIME_STEPS: dict[int, float] = {
    0: 1,
    1: 20,
    2: 600,
}

MINIMUM_WINDOWS_SCROLL_VALUE: int = 120
FACTOR_LARGE_SCROLLING: int = 10


LEFT_MOUSE_UP: str = "#left mouse button#"
RIGHT_MOUSE_UP: str = "#right mouse button#"
MOUSE_WHEEL_UP: str = "#middle mouse button#"

KEY_NAME_CORRECTION: dict[str, str] = {
    LEFT_MOUSE_UP: "<ButtonRelease-1>",
    RIGHT_MOUSE_UP: "<ButtonRelease-2>" if ON_MAC else "<ButtonRelease-3>",
    MOUSE_WHEEL_UP: "<ButtonRelease-3>" if ON_MAC else "<ButtonRelease-2>",
}


@dataclass
class TkEvents:
    """
    Class holding tkinter events as class properties.
    The strings behind some of the events depend on the platform the software is
    running on (Linux, Mac, or Windows).
    """

    RIGHT_BUTTON_DOWN: ClassVar[str] = "<Button-2>" if ON_MAC else "<Button-3>"
    RIGHT_BUTTON_UP: ClassVar[str] = KEY_NAME_CORRECTION[RIGHT_MOUSE_UP]
    MIDDLE_BUTTON_DOWN: ClassVar[str] = "<Button-3>" if ON_MAC else "<Button-2>"
    MIDDLE_BUTTON_UP: ClassVar[str] = KEY_NAME_CORRECTION[MOUSE_WHEEL_UP]
    LEFT_BUTTON_DOWN: ClassVar[str] = "<Button-1>"
    LEFT_BUTTON_UP: ClassVar[str] = KEY_NAME_CORRECTION[LEFT_MOUSE_UP]
    LEFT_BUTTON_DOUBLE: ClassVar[str] = "<Double-1>"
    MOUSE_MOTION: ClassVar[str] = "<Motion>"
    MOUSE_MOTION_WHILE_LEFT_BUTTON_DOWN: ClassVar[str] = "<B1-Motion>"
    MOUSE_ENTERS_WIDGET: ClassVar[str] = "<Enter>"
    MOUSE_LEAVES_WIDGET: ClassVar[str] = "<Leave>"
    TREEVIEW_SELECT: ClassVar[str] = "<<TreeviewSelect>>"
    PLUS_KEY: ClassVar[str] = "+"
    KEYPAD_PLUS_KEY: ClassVar[str] = "<KP_Add>"
    LEFT_ARROW_KEY: ClassVar[str] = "<Left>"
    RIGHT_ARROW_KEY: ClassVar[str] = "<Right>"
    UP_ARROW_KEY: ClassVar[str] = "<Up>"
    DOWN_ARROW_KEY: ClassVar[str] = "<Down>"
    RETURN_KEY: ClassVar[str] = "<Return>"
    KEYPAD_RETURN_KEY: ClassVar[str] = "<KP_Enter>"
    DELETE_KEY: ClassVar[str] = "<Delete>"
    BACKSPACE_KEY: ClassVar[str] = "<BackSpace>"
    SPACE_KEY: ClassVar[str] = "<space>"
    ESCAPE_KEY: ClassVar[str] = "<Escape>"
    ALPHANUMERIC_KEY: ClassVar[str] = "<Key>"
    MULTI_SELECT_SINGLE: ClassVar[str] = (
        "<Command-ButtonRelease-1>" if ON_MAC else "<Control-ButtonRelease-1>"
    )
    MOUSE_WHEEL_SCROLLED: ClassVar[str] = "<MouseWheel>"
    CONTROL_LEFT: ClassVar[str] = "<Control_L>"
    CONTROL_RIGHT: ClassVar[str] = "<Control_R>"

    def get_key_assignment(self) -> None:
        self.key_assignment: dict[str, str] = {
            self.RIGHT_BUTTON_DOWN: "",
            RIGHT_MOUSE_UP: "finish active count if possible",
            self.MIDDLE_BUTTON_DOWN: "",
            MOUSE_WHEEL_UP: (
                f"Squitch beween 1 and "
                f"{str(FACTOR_LARGE_SCROLLING)}"
                f" frames as small jumps"
            ),
            self.LEFT_BUTTON_DOWN: "",
            LEFT_MOUSE_UP: "Set new Event for the Active Count",
            self.LEFT_BUTTON_DOUBLE: "",
            self.MOUSE_MOTION: "",
            self.MOUSE_MOTION_WHILE_LEFT_BUTTON_DOWN: "",
            self.MOUSE_ENTERS_WIDGET: "",
            self.MOUSE_LEAVES_WIDGET: "",
            self.TREEVIEW_SELECT: "",
            self.PLUS_KEY: "",
            self.KEYPAD_PLUS_KEY: "",
            self.LEFT_ARROW_KEY: "Big jump backward in the videos",
            self.RIGHT_ARROW_KEY: "Big jump forward in the videos",
            self.UP_ARROW_KEY: "",
            self.DOWN_ARROW_KEY: "",
            self.RETURN_KEY: "Finish active count if possible",
            self.KEYPAD_RETURN_KEY: "",
            self.DELETE_KEY: "Delete selected counts",
            self.BACKSPACE_KEY: "Delete selected counts",
            self.SPACE_KEY: "Small jump forward",
            self.ESCAPE_KEY: "Abort active count",
            self.MULTI_SELECT_SINGLE: "",
            self.MOUSE_WHEEL_SCROLLED: "Small jump forward / backward in the videos",
            self.CONTROL_LEFT: "",
            self.CONTROL_RIGHT: "",
        }


tk_events = TkEvents()
tk_events.get_key_assignment()
