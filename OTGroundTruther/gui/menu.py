from tkinter import Menu
from typing import Any

from OTGroundTruther.gui.presenter_interface import PresenterInterface


class MenuBar(Menu):
    def __init__(self, presenter: PresenterInterface, **kwargs: Any):
        super().__init__(**kwargs)
        self._presenter = presenter
        self._get_widgets()
        self._place_widgets()

    def _get_widgets(self) -> None:
        self._file_menu = FileMenu(master=self, tearoff=0, presenter=self._presenter)
        self._help_menu = HelpMenu(master=self, tearoff=0, presenter=self._presenter)

    def _place_widgets(self) -> None:
        self.add_cascade(label="File", menu=self._file_menu)
        self.add_cascade(label="Help", menu=self._help_menu)


class FileMenu(Menu):
    def __init__(self, presenter: PresenterInterface, **kwargs: Any):
        super().__init__(**kwargs)
        self._presenter = presenter
        self._get_and_place_widgets()

    def _get_and_place_widgets(self) -> None:
        self.add_command(label="Load Videos", command=self._presenter.load_video_files)
        self.add_command(label="Load otflow", command=self._presenter.load_otflow)
        self.add_command(label="Load Events", command=self._presenter.load_events)
        self.add_command(label="Save Events", command=self._presenter.save_events)


class HelpMenu(Menu):
    def __init__(self, presenter: PresenterInterface, **kwargs: Any):
        super().__init__(**kwargs)
        self._presenter = presenter
        self._get_and_place_widgets()

    def _get_and_place_widgets(self) -> None:
        self.add_command(
            label="Key Assignment", command=self._presenter.show_key_assignment
        )
