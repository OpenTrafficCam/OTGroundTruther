from abc import ABC, abstractmethod

from .presenter import Presenter


class Gui(ABC):
    @abstractmethod
    def introduce_presenter(self, presenter: Presenter) -> None:
        raise NotImplementedError

    def init_widgets(self) -> None:
        raise NotImplementedError

    def place_widgets(self) -> None:
        raise NotImplementedError

    def mainloop(self) -> None:
        raise NotImplementedError
