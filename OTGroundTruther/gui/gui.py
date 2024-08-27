from typing import Any

import customtkinter as ctk
from CTkMessagebox import CTkMessagebox

from OTGroundTruther.gui.constants import PADX, PADY, tk_events
from OTGroundTruther.gui.frame_canvas import FrameCanvas
from OTGroundTruther.gui.frame_treeview_counts import FrameTreeview
from OTGroundTruther.gui.key_assignment import KeyAssignmentWindow
from OTGroundTruther.gui.menu import MenuBar
from OTGroundTruther.gui.presenter_interface import PresenterInterface

TITLE: str = "OTGroundTruther"
DELETE_BUTTON_TXT: str = "Delete"


class Gui(ctk.CTk):
    def __init__(self, presenter: PresenterInterface, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._presenter = presenter
        self._event_translator = GuiEventTranslator(gui=self, presenter=self._presenter)

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

    def build_key_assignment_window(self, key_assignment_text: dict[str, str]) -> None:
        self.key_assigment_window = KeyAssignmentWindow(
            master=self,
            key_assignment_text=key_assignment_text,
            presenter=self._presenter,
        )

    def ask_if_keep_existing_counts(self) -> bool:
        msg = CTkMessagebox(
            title="Keep existing Counts?",
            message="Do you want to keep the already existing counts and sections?",
            icon="question",
            option_1="Yes",
            option_2="No",
        )
        keep_existing = msg.get()
        print(keep_existing)
        if keep_existing == "Yes":
            return True
        else:
            return False

    def get_new_suffix_for_new_counts(self):
        print("hello")
        self.subwindow = ctk.CTkToplevel(self)
        self.subwindow.title("Suffix for the counts of the file")
        ctk.CTkLabel(
            self.subwindow, text="Enter the suffix for the counts of the file."
        )
        self.entry = ctk.CTkEntry(self.subwindow)
        self.entry.pack(pady=5)
        ctk.CTkButton(
            self.subwindow, text="OK", command=self.get_suffix_and_add_counts
        ).pack(pady=10)

    def get_suffix_and_add_counts(self) -> None:
        user_input = self.entry.get()
        self.subwindow.destroy()
        self._presenter.load_counts_with_suffix(suffix=user_input)


class GuiEventTranslator:
    def __init__(self, gui: Gui, presenter: PresenterInterface):
        self._gui = gui
        self._presenter = presenter
        self._bind_events()

    def _bind_events(self) -> None:
        self._gui.bind(tk_events.DELETE_KEY, self._on_delete_key)
        self._gui.bind(tk_events.BACKSPACE_KEY, self._on_delete_key)

    def _on_delete_key(self, event: Any) -> None:
        self._presenter.delete_selected_counts()
