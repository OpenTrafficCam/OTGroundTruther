from typing import Any

import customtkinter as ctk  # type: ignore

from OTGroundTruther.gui.constants import PADX, PADY, STICKY
from OTGroundTruther.gui.presenter_interface import PresenterInterface

KEY_ASSIGNMENT_KEYS: str = "keys"
KEY_ASSIGNMENT_ACTIONS: str = "actions"


class KeyAssignmentWindow(ctk.CTkToplevel):
    def __init__(
        self,
        presenter: PresenterInterface,
        key_assignment_text: dict[str, str],
        **kwargs: Any
    ):
        super().__init__(**kwargs)
        self._presenter = presenter
        self.title("Key Assignment")
        self.show_key_assignment_in_label(key_assignment_text=key_assignment_text)
        self.lift()

    def show_key_assignment_in_label(self, key_assignment_text):
        self.label_action = ctk.CTkLabel(
            self, text=key_assignment_text[KEY_ASSIGNMENT_ACTIONS], justify="right"
        )
        self.label_action.grid(
            row=0,
            column=0,
            padx=PADX,
            pady=PADY,
            sticky=STICKY,
        )
        self.label_key = ctk.CTkLabel(
            self, text=key_assignment_text[KEY_ASSIGNMENT_KEYS], justify="left"
        )
        self.label_key.grid(
            row=0,
            column=1,
            padx=PADX,
            pady=PADY,
            sticky=STICKY,
        )
