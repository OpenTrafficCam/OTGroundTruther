from abc import ABC, abstractmethod


class PresenterInterface(ABC):
    @abstractmethod
    def handle_gui_input(self, event=None) -> None:
        raise NotImplementedError
