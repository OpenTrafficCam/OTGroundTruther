import tkinter.ttk as ttk
from typing import Any

import customtkinter as ctk

from OTGroundTruther.gui.constants import PADX, PADY, STICKY
from OTGroundTruther.gui.presenter_interface import PresenterInterface
from OTGroundTruther.model.count import CountRepository

FRAME_TREEVIEW_ROW = 1
FRAME_TREEVIEW_COLUMN = 0


class FrameTreeview(ctk.CTkFrame):
    def __init__(self, presenter: PresenterInterface, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._presenter = presenter
        self.columnconfigure(1)
        self._get_widgets()
        self._place_widgets()

    def _get_widgets(self) -> None:
        self.treeview_count = Treeview(
            master=self, presenter=self._presenter, columns=("id", "class")
        )

    def _place_widgets(self) -> None:
        self.treeview_count.grid(
            row=FRAME_TREEVIEW_ROW,
            column=FRAME_TREEVIEW_COLUMN,
            padx=PADX,
            pady=PADY,
            sticky=STICKY,
        )


class Treeview(ttk.Treeview):
    def __init__(self, presenter: PresenterInterface, **kwargs: Any):
        super().__init__(**kwargs)
        self._presenter = presenter
        # self._event_translator = CanvasEventTranslator(
        #     canvas=self, presenter=self._presenter
        # )
        self.heading("id", text="ID")
        self.heading("class", text="Class")
        self._current_id: Any = None

    def update_treeview(self, count_repository: CountRepository) -> None:
        for count in count_repository.get_all_as_list():
            self.insert(
                parent="",
                index=count.get_road_user_id(),
                text=str(count.get_road_user_id()),
                values=[count.get_road_user_class().get_short_label()],
            )
