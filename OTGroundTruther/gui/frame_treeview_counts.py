import tkinter as tk
import tkinter.ttk as ttk
from typing import Any

import customtkinter as ctk

from OTGroundTruther.gui.constants import PADX, PADY, STICKY
from OTGroundTruther.gui.presenter_interface import PresenterInterface
from OTGroundTruther.model.count import (
    COUNT_CLASS_NAME,
    COUNT_ENTER_GATE_NAME,
    COUNT_ENTER_TIME_NAME,
    COUNT_EXIT_GATE_NAME,
    COUNT_EXIT_TIME_NAME,
    COUNT_ID_NAME,
    Count,
    CountRepository,
)

TREEVIEW_FRAME_ROW: int = 0
TREEVIEW_FRAME_COLUMN: int = 0

TREEVIEW_SELECT: str = "<<TreeviewSelect>>"

COUNT_PROPERTIES_ORDER: list[str] = [
    COUNT_ID_NAME,
    COUNT_CLASS_NAME,
    COUNT_ENTER_TIME_NAME,
    COUNT_ENTER_GATE_NAME,
    COUNT_EXIT_TIME_NAME,
    COUNT_EXIT_GATE_NAME,
]
COLUMN_WIDTHS: dict[str, int] = {
    COUNT_ID_NAME: 40,
    COUNT_CLASS_NAME: 100,
    COUNT_ENTER_TIME_NAME: 100,
    COUNT_ENTER_GATE_NAME: 80,
    COUNT_EXIT_TIME_NAME: 100,
    COUNT_EXIT_GATE_NAME: 80,
}


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
            columns=COUNT_PROPERTIES_ORDER,
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
        self.add_columns()

        self.add_scrollbar()
        self._event_translator = TreeviewTranslator(
            treeview=self, presenter=self._presenter
        )
        self.add_next_column_sort_direction()

    def add_columns(self) -> None:
        for key in COUNT_PROPERTIES_ORDER:
            self.heading(key, text=key)
            self.column(key, width=COLUMN_WIDTHS[key])

    def add_scrollbar(self) -> None:
        self.scrollbar = ctk.CTkScrollbar(
            master=self.master, orientation=ctk.VERTICAL, command=self.yview
        )
        self.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.grid(
            row=TREEVIEW_FRAME_ROW, column=TREEVIEW_FRAME_COLUMN + 1, sticky="ns"
        )

    def add_next_column_sort_direction(self):
        self.next_column_sort_direction = {}
        for column in COUNT_PROPERTIES_ORDER:
            self.next_column_sort_direction[column] = False

    def refresh_treeview(self, count_repository: CountRepository) -> None:
        for count_id, count in count_repository.get_all_as_dict().items():
            self.add_count(count=count)

    def add_count(self, count: Count) -> None:
        properties_random_order = count.get_properties_to_show_as_dict()
        properties_in_correct_order: dict[str, str] = {}
        for count_property in COUNT_PROPERTIES_ORDER:
            properties_in_correct_order[count_property] = properties_random_order[
                count_property
            ]
        self.insert(
            parent="",
            index=tk.END,
            iid=str(count.get_road_user_id()),
            values=list(properties_in_correct_order.values()),
        )
        self.scroll_to_the_end()

    def delete_selected_count(self) -> list[int]:
        to_delete_count_ids = []
        for selected_count_id in self.selection():
            self.delete(selected_count_id)
            to_delete_count_ids.append(int(selected_count_id))
        return to_delete_count_ids

    def get_selected_count_ids(self) -> list[int]:
        return [int(count_id) for count_id in self.selection()]

    def sort_by_column(self, sort_column: str) -> None:
        column_values_and_row_index = [
            (self.set(tv_index, sort_column), tv_index)
            for tv_index in self.get_children("")
        ]
        column_values_and_row_index.sort(
            reverse=self.next_column_sort_direction[sort_column]
        )
        # rearrange items in sorted positions
        for order_index, (value, tv_index) in enumerate(column_values_and_row_index):
            self.move(tv_index, "", order_index)
        self.update_next_column_sort_direction(sort_column=sort_column)

    def update_next_column_sort_direction(self, sort_column: str) -> None:
        self.next_column_sort_direction[
            sort_column
        ] = not self.next_column_sort_direction[sort_column]
        for column in COUNT_PROPERTIES_ORDER:
            if column != sort_column:
                self.next_column_sort_direction[column] = False

    def scroll_to_the_end(self) -> None:
        self.yview_moveto(1)


class TreeviewTranslator:
    def __init__(self, treeview: Treeview, presenter: PresenterInterface):
        self._treeview = treeview
        self._presenter = presenter
        self._bind_events()

    def _bind_events(self) -> None:
        self._treeview.bind(TREEVIEW_SELECT, self._show_selected_count)

        for column in COUNT_PROPERTIES_ORDER:
            self._treeview.heading(
                column,
                text=column,
                command=lambda _column=column: self._treeview.sort_by_column(_column),
            )

    def _show_selected_count(self, event: Any) -> None:
        selected_count_ids = self._treeview.get_selected_count_ids()
        if selected_count_ids:
            self._presenter.show_start_of_count(selected_count_ids[0])
