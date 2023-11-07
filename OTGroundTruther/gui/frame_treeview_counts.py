import tkinter.ttk as ttk
from typing import Any

import customtkinter as ctk

from OTGroundTruther.gui.constants import PADX, PADY, STICKY
from OTGroundTruther.gui.presenter_interface import PresenterInterface
from OTGroundTruther.model.count import Count, CountRepository

TREEVIEW_FRAME_ROW = 0
TREEVIEW_FRAME_COLUMN = 0

COLUMNS_HEADINGS = {"ID": "ID", "Class": "Class", "Starttime": "Starttime"}


class FrameTreeview(ctk.CTkFrame):
    def __init__(self, presenter: PresenterInterface, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._presenter = presenter
        self.columnconfigure(1)
        self._get_widgets()
        self._place_widgets()

    def _get_widgets(self) -> None:
        self.treeview_count = Treeview(
            master=self,
            presenter=self._presenter,
            columns=list(COLUMNS_HEADINGS.keys()),
            show="headings",
        )

    def _place_widgets(self) -> None:
        self.treeview_count.grid(
            row=TREEVIEW_FRAME_ROW,
            column=TREEVIEW_FRAME_COLUMN,
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
        for key, value in COLUMNS_HEADINGS.items():
            self.heading(key, text=value)
        self._current_id: Any = None
        self.add_scrollbar()
        self.counts_line_ids: dict[str, int] = {}

    def add_scrollbar(self) -> None:
        self.scrollbar = ctk.CTkScrollbar(
            master=self.master, orientation=ctk.VERTICAL, command=self.yview
        )
        self.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.grid(
            row=TREEVIEW_FRAME_ROW, column=TREEVIEW_FRAME_COLUMN + 1, sticky="ns"
        )

    def refresh_treeview(self, count_repository: CountRepository) -> None:
        for count_id, count in count_repository.get_all_as_dict().items():
            line_id = self.add_count(count)
            self.counts_line_ids[line_id] = count_id

    def add_count(self, count: Count) -> str:
        return self.insert(
            parent="",
            index=count.get_road_user_id(),
            # text=str(count.get_road_user_id()),
            values=[
                count.get_road_user_id(),
                count.get_road_user_class().get_short_label(),
                count.get_first_event().get_time_as_str(),
            ],
        )

    def delete_selected_count(self) -> list[int]:
        to_delete_count_ids = []
        for selected_line_id in self.selection():
            self.delete(selected_line_id)
            to_delete_count_ids.append(self.counts_line_ids[selected_line_id])
            del self.counts_line_ids[selected_line_id]
        return to_delete_count_ids
