from dataclasses import dataclass
from typing import ClassVar

from OTGroundTruther.model.config import ON_MAC

PADX = 10
PADY = 5
STICKY = "NESW"

STATE_DISABLED = "disabled"
STATE_NORMAL = "normal"


@dataclass
class TkEvents:
    """
    Class holding tkinter events as class properties.
    The strings behind some of the events depend on the platform the software is
    running on (Linux, Mac, or Windows).
    """

    RIGHT_BUTTON_DOWN: ClassVar[str] = "<Button-2>" if ON_MAC else "<Button-3>"
    RIGHT_BUTTON_UP: ClassVar[str] = (
        "<ButtonRelease-2>" if ON_MAC else "<ButtonRelease-3>"
    )
    MIDDLE_BUTTON_DOWN: ClassVar[str] = "<Button-3>" if ON_MAC else "<Button-2>"
    MIDDLE_BUTTON_UP: ClassVar[str] = (
        "<ButtonRelease-3>" if ON_MAC else "<ButtonRelease-2>"
    )
    LEFT_BUTTON_DOWN: ClassVar[str] = "<Button-1>"
    LEFT_BUTTON_UP: ClassVar[str] = "<ButtonRelease-1>"
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


tk_events = TkEvents()
