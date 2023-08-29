from abc import ABC, abstractmethod

class PresenterInterfaceForCanvasInputHandler(ABC):
    @abstractmethod
    def 



class CanvasInputHandler:
    def on_mouse_scrolled(self, scroll_delta: int) -> None:
        print(f"Mouse scrolled: {scroll_delta}")
        self._

    def on_mouse_pressed_and_scrolled(self, scroll_delta: int) -> None:
        print(f"Mouse pressed and scrolled: {scroll_delta}")

    def on_left_button_down(self, coordinate: tuple[int, int]) -> None:
        pass

    def on_rigth_button_down(self, coordinate: tuple[int, int]) -> None:
        pass

    def on_alphanumeric_key(self, key_symbol: str) -> None:
        print(f"Alphanumeric key: {key_symbol}")
