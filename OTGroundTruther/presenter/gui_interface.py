from abc import ABC, abstractmethod

from OTGroundTruther.presenter.presenter import Presenter


class GuiInterface(ABC):
    @abstractmethod
    def introduce_presenter(self, presenter: Presenter) -> None:
        raise NotImplementedError

    @abstractmethod
    def run(self) -> None:
        raise NotImplementedError
