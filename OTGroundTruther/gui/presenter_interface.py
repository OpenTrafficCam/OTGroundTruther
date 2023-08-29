from abc import ABC, abstractmethod


class PresenterInterface(ABC):
    @abstractmethod
    def load_video_files(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def scroll_through_videos(
        self, scroll_delta: int, mouse_wheel_pressed: bool
    ) -> None:
        raise NotImplementedError
