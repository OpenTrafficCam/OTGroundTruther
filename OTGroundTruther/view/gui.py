import customtkinter as ctk

from .constants import PADX, PADY
from .frame_canvas import FrameCanvas
from .presenter_interface import PresenterInterface

TITLE: str = "OTGroundTruther"
DELETE_BUTTON_TXT: str = "Delete"


class Gui(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()
        self.presenter: PresenterInterface | None = None
        self.title(TITLE)
        self.geometry("500x300")
        self.get_widgits()
        self.place_widgets()

    def get_widgits(self) -> None:
        self.frame_canvas = FrameCanvas(self, padx=PADX, pady=PADY)

    def place_widgets(self) -> None:
        self.frame_canvas.pack(fill=ctk.BOTH, expand=True)

    def introduce_presenter(self, presenter: PresenterInterface) -> None:
        self.presenter = presenter
