import copy
import tkinter as tk
import tkinter.ttk as ttk
from typing import Any

import customtkinter as ctk
from PIL import Image

from OTGroundTruther.gui.constants import PADX, PADY, STICKY
from OTGroundTruther.gui.presenter_interface import PresenterInterface
from OTGroundTruther.model.count import (
    COUNT_CLASS_NAME,
    COUNT_ENTER_GATE_NAME,
    COUNT_ENTER_TIME_NAME,
    COUNT_EXIT_GATE_NAME,
    COUNT_ID_NAME,
    COUNT_TIME_SPAN,
    Count,
    CountRepository,
)
from OTGroundTruther.model.road_user_class import RoadUserClass

COMBOBOX_FRAME_ROW: int = 0
COMBOBOX_FRAME_COLUMN: int = 0

TREEVIEW_FRAME_ROW: int = COMBOBOX_FRAME_ROW + 1
TREEVIEW_FRAME_COLUMN: int = COMBOBOX_FRAME_COLUMN

CLASS_LABEL_FRAME_ROW: int = TREEVIEW_FRAME_ROW + 1
CLASS_LABEL_FRAME_COLUMN: int = COMBOBOX_FRAME_COLUMN

TREEVIEW_SELECT: str = "<<TreeviewSelect>>"

COUNT_PROPERTIES_ORDER: list[str] = [
    COUNT_ID_NAME,
    COUNT_CLASS_NAME,
    COUNT_ENTER_TIME_NAME,
    COUNT_ENTER_GATE_NAME,
    COUNT_EXIT_GATE_NAME,
    COUNT_TIME_SPAN,
]
COLUMN_WIDTHS: dict[str, int] = {
    COUNT_ID_NAME: 40,
    COUNT_CLASS_NAME: 100,
    COUNT_ENTER_TIME_NAME: 100,
    COUNT_ENTER_GATE_NAME: 80,
    COUNT_EXIT_GATE_NAME: 80,
    COUNT_TIME_SPAN: 80,
}

ALL_CLASSES_SELECTION: str = "All"
CLASS_GROUPS: dict[str, list[str]] = {
    "All Pedestrians, Bicyclists, Scooter Drivers": [
        "pedestrian",
        "bicyclist",
        "bicyclist_with_trailer",
        "cargo_bike_driver",
        "scooter_driver",
    ],
    "All Bicyclists": ["bicyclist", "bicyclist_with_trailer", "cargo_bike_driver"],
    "Motorised Vehicles": [
        "train",
        "truck_with_semitrailer",
        "truck_with_trailer",
        "truck",
        "bus",
        "delivery_van_with_trailer",
        "delivery_van",
        "private_van_with_trailer",
        "private_van",
        "car_with_trailer",
        "car",
        "motorcyclist",
    ],
    "Light Vehicles": [
        "delivery_van_with_trailer",
        "delivery_van",
        "private_van_with_trailer",
        "private_van",
        "car_with_trailer",
        "car",
        "motorcyclist",
    ],
    "Heavy Vehicles": ["truck_with_semitrailer", "truck_with_trailer", "truck", "bus"],
    "All Trucks": ["truck_with_semitrailer", "truck_with_trailer", "truck"],
}


class FrameTreeview(ctk.CTkFrame):
    def __init__(self, presenter: PresenterInterface, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._presenter = presenter
        self.columnconfigure(1)
        self._get_widgets()
        self._place_widgets()

    def _get_widgets(self) -> None:
        self.combobox_counts = Combobox(
            master=self, presenter=self._presenter, state="readonly"
        )
        self.treeview_counts = Treeview(
            master=self,
            presenter=self._presenter,
            columns=COUNT_PROPERTIES_ORDER,
            show="headings",
        )
        self.class_label = ClassLabel(
            master=self,
            presenter=self._presenter,
            text="",
        )

    def _place_widgets(self) -> None:
        self.treeview_counts.grid(
            row=TREEVIEW_FRAME_ROW,
            column=TREEVIEW_FRAME_COLUMN,
            padx=PADX,
            pady=PADY,
            sticky=STICKY,
        )
        self.combobox_counts.grid(
            row=COMBOBOX_FRAME_ROW,
            column=COMBOBOX_FRAME_COLUMN,
            padx=PADX,
            pady=PADY,
            sticky=STICKY,
        )
        self.class_label.grid(
            row=CLASS_LABEL_FRAME_ROW,
            column=CLASS_LABEL_FRAME_COLUMN,
            padx=PADX,
            pady=PADY,
            sticky=STICKY,
        )


class Combobox(ctk.CTkComboBox):
    def __init__(self, presenter: PresenterInterface, **kwargs: Any):
        super().__init__(**kwargs)
        self._presenter = presenter
        self.combobox_var = ctk.StringVar()

    def fill_and_set(self, class_names: list[str]) -> None:
        self.class_names = class_names
        self.configure(
            variable=self.combobox_var,
            values=[ALL_CLASSES_SELECTION] + list(CLASS_GROUPS.keys()) + class_names,
            command=self.combobox_callback,
        )
        self.set(value=ALL_CLASSES_SELECTION)
        self.selected_classes: list[str] = copy.deepcopy(class_names)

    def combobox_callback(self, selected_option: str) -> None:
        if selected_option == ALL_CLASSES_SELECTION:
            self.selected_classes = self.class_names
        elif selected_option in list(CLASS_GROUPS.keys()):
            self.selected_classes = CLASS_GROUPS[selected_option]
        else:
            self.selected_classes = [selected_option]
        self._presenter.update_canvas_image_with_new_overlay()
        self._presenter.refresh_treeview()

    def get_selected_classes(self) -> list[str]:
        return self.selected_classes


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
        self.delete(*self.get_children())
        selected_classes = self._presenter.get_selected_classes_from_gui()
        for count in count_repository.get_all_as_dict().values():
            if count.get_road_user_class().get_name() in selected_classes:
                self.add_count(
                    count=count,
                )

    def add_and_select_count_if_in(self, count: Count) -> None:
        if (
            count.get_road_user_class().get_name()
            in self._presenter.get_selected_classes_from_gui()
        ):
            self.add_count(count=count)
            self.selection_set([str(count.get_road_user_id())])
        else:
            self._presenter.update_canvas_image_with_new_overlay()

    def add_count(self, count: Count) -> None:
        properties_random_order = count.get_properties_to_show_as_dict()
        values_in_correct_order: list[str] = []
        for count_property in COUNT_PROPERTIES_ORDER:
            values_in_correct_order.append(properties_random_order[count_property])

        self.insert(
            parent="",
            index=tk.END,
            iid=str(count.get_road_user_id()),
            values=list(values_in_correct_order),
        )
        self.scroll_to_the_end()

    def delete_selected_count(self) -> None:
        for selected_count_id in self.selection():
            self.delete(selected_count_id)

    def get_selected_count_ids(self) -> list[str]:
        return list(self.selection())

    def sort_by_column(self, sort_column: str) -> None:
        column_values_and_row_index = [
            (self.set(tv_index, sort_column), tv_index)
            for tv_index in self.get_children("")
        ]
        column_values_and_row_index.sort(
            reverse=self.next_column_sort_direction[sort_column]
        )
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
            self._presenter.show_start_of_count(count_id=selected_count_ids[0])
            self._presenter.show_class_image_by_count_id(count_id=selected_count_ids[0])


class ClassLabel(ctk.CTkLabel):
    def __init__(self, presenter: PresenterInterface, **kwargs: Any):
        super().__init__(**kwargs)
        self._presenter = presenter

    def show_class_img(self, road_user_class: RoadUserClass):
        self.image = ctk.CTkImage(light_image=road_user_class.get_icon(), size=(80, 80))
        self.configure(image=self.image)

    def set_blank(self):
        white_image = Image.new("RGB", (1, 1), color="white")
        white_image_tk = ctk.CTkImage(light_image=white_image, size=(1, 1))

        self.configure(image=white_image_tk)
        self.image = white_image_tk
