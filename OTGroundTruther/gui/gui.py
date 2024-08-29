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

SUBW_KEEPEXISTINGCOUNTS_TITLE: str = "Keep existing Counts?"
SUBW_KEEPEXISTINGCOUNTS_QUESTION: str = (
    "Do you want to keep the already existing counts and sections?"
)
SUBW_KEEPEXISTINGCOUNTS_ICON: str = "question"
SUBW_KEEPEXISTINGCOUNTS_KEEP: str = "Yes"
SUBW_KEEPEXISTINGCOUNTS_CLEAR: str = "No"

SUBW_ENTERSUFFIXCOUNTS_TITLE: str = "Suffix for the counts of the file"
SUBW_ENTERSUFFIXCOUNTS_INSTRUCTION: str = "Enter a suffix for the counts of the file."


SUBW_SECTIONS_NOT_COMPARTIBLE_TITLE: str = "Sections are not compatible."
SUBW_SECTIONS_NOT_COMPARTIBLE_INFO: str = (
    "The sections from the file are not compatible with the existing "
    + "sections. Therefore the existing sections and counts got deleted."
)
SUBW_SECTIONS_NOT_COMPARTIBLE_ICON: str = "info"


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
            master=self,
            title=SUBW_KEEPEXISTINGCOUNTS_TITLE,
            message=SUBW_KEEPEXISTINGCOUNTS_QUESTION,
            icon=SUBW_KEEPEXISTINGCOUNTS_ICON,
            option_1=SUBW_KEEPEXISTINGCOUNTS_CLEAR,
            option_2=SUBW_KEEPEXISTINGCOUNTS_KEEP,
        )
        keep_existing = msg.get()
        if keep_existing == SUBW_KEEPEXISTINGCOUNTS_KEEP:
            return True
        else:
            return False

    def get_new_suffix_for_new_counts(self) -> None:
        self.subwindow = EnteringStringSubwindow(
            self,
            title=SUBW_ENTERSUFFIXCOUNTS_TITLE,
            label=SUBW_ENTERSUFFIXCOUNTS_INSTRUCTION,
        )

    def inform_user_sections_not_compatible(self) -> None:
        self.subwindow = CTkMessagebox(
            master=self,
            title=SUBW_SECTIONS_NOT_COMPARTIBLE_TITLE,
            message=SUBW_SECTIONS_NOT_COMPARTIBLE_INFO,
            icon=SUBW_SECTIONS_NOT_COMPARTIBLE_ICON,
        )


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


class EnteringStringSubwindow(ctk.CTkToplevel):
    def __init__(self, gui: Gui, title: str, label: str) -> None:
        super().__init__(gui)
        self._gui = gui
        self.title(title)
        ctk.CTkLabel(self, text=label).pack(pady=0)
        self.entry = ctk.CTkEntry(self)
        self.entry.pack(pady=5)
        ctk.CTkButton(self, text="OK", command=self._get_suffix_and_add_counts).pack(
            pady=10
        )
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.transient(gui)
        self.grab_set()
        gui.wait_window(self)

    def _get_suffix_and_add_counts(self) -> None:
        user_input = self.entry.get()
        self.destroy()
        self._gui._presenter.load_counts_with_suffix(suffix=user_input)

    def on_close(self):
        self.destroy()
