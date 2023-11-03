from typing import Any

import customtkinter as ctk

from OTGroundTruther.gui.constants import PADX, PADY
from OTGroundTruther.gui.frame_canvas import FrameCanvas
from OTGroundTruther.gui.frame_treeview_counts import FrameTreeview
from OTGroundTruther.gui.menu import MenuBar
from OTGroundTruther.gui.presenter_interface import PresenterInterface

TITLE: str = "OTGroundTruther"
DELETE_BUTTON_TXT: str = "Delete"


class Gui(ctk.CTk):
    def __init__(self, presenter: PresenterInterface, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._presenter = presenter

    def run(self):
        self.title(TITLE)
        self._maximize_window()
        self._get_widgets()
        self._place_widgets()
        self.after(ms=1000, func=self._presenter.after_run_gui)
        self.mainloop()

    def _maximize_window(self):
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        self.geometry(f"{screen_width}x{screen_height}+0+0")

    def _get_widgets(self) -> None:
        self.menu_bar = MenuBar(master=self, presenter=self._presenter)
        self.frame_canvas = FrameCanvas(master=self, presenter=self._presenter)
        self.frame_treeview = FrameTreeview(master=self, presenter=self._presenter)

    def _place_widgets(self) -> None:
        self.config(menu=self.menu_bar)
        self.frame_canvas.pack(
            side=ctk.LEFT, fill=ctk.BOTH, expand=True, padx=PADX, pady=PADY
        )
        self.frame_treeview.pack(
            side=ctk.RIGHT, fill=ctk.BOTH, expand=True, padx=PADX, pady=PADY
        )
