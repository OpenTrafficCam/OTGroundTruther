from pathlib import Path
from typing import Any

import customtkinter as ctk
from PIL import Image, ImageTk

from OTGroundTruther.gui.constants import PADX, STICKY, tk_events
from OTGroundTruther.gui.presenter_interface import PresenterInterface
from OTGroundTruther.model.config import ON_WINDOWS

PREVIEW_IMAGE_FILE: str = r"assets/OpenTrafficCam_800.png"
JUMP_TIME_STEPS: dict[int, float] = {
    0: 1,
    1: 20,
    2: 600,
}


class FrameCanvas(ctk.CTkFrame):
    def __init__(self, presenter: PresenterInterface, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._presenter = presenter
        self._get_widgets()
        self._place_widgets()

    def _get_widgets(self) -> None:
        self.canvas_background = CanvasBackground(
            master=self, presenter=self._presenter
        )

    def _place_widgets(self) -> None:
        PADY = 10
        self.canvas_background.grid(
            row=2, column=0, padx=PADX, pady=PADY, sticky=STICKY
        )

    def clear_image(self) -> None:
        self.canvas_background.clear_image()


class CanvasBackground(ctk.CTkCanvas):
    def __init__(self, presenter: PresenterInterface, **kwargs: Any):
        super().__init__(**kwargs)
        self._presenter = presenter
        self._event_translator = CanvasEventTranslator(
            canvas=self, presenter=self._presenter
        )

        self._current_image: ImageTk.PhotoImage
        self._current_id: Any = None
        self.update_image(self._get_preview_image())

    def _get_preview_image(self) -> Image.Image:
        if Path(PREVIEW_IMAGE_FILE).exists():
            return Image.open(PREVIEW_IMAGE_FILE)

    def update_image(self, image: Image.Image) -> None:
        photo_image = ImageTk.PhotoImage(image)
        if self._current_id:
            self.delete(self._current_id)
        self._current_image = photo_image
        self.resize_canvas_by_image()
        self._draw()

    def resize_canvas_by_image(self):
        self.config(
            width=self._current_image.width(), height=self._current_image.height()
        )

    def _draw(self) -> None:
        self._current_id = self.create_image(
            0, 0, image=self._current_image, anchor=ctk.NW
        )
        self.config(
            width=self._current_image.width(), height=self._current_image.height()
        )
        self.config(highlightthickness=0)

    def _get_width(self) -> int:
        return self.winfo_width()

    def _get_height(self) -> int:
        return self.winfo_height()

    def clear_image(self) -> None:
        if self._current_id:
            self.delete(self._current_id)


class CanvasEventTranslator:
    def __init__(self, canvas: CanvasBackground, presenter: PresenterInterface):
        self._canvas = canvas
        self._presenter = presenter
        self._middle_button_pressed: bool = False
        self._current_jump_time_step: int = 0
        self._bind_events()

    def _bind_events(self) -> None:
        self._canvas.bind(tk_events.LEFT_BUTTON_DOWN, self._on_left_button_down)
        self._canvas.bind(tk_events.LEFT_BUTTON_UP, self._on_left_button_up)
        self._canvas.bind(tk_events.RIGHT_BUTTON_UP, self._on_right_button_up)
        self._canvas.bind(tk_events.MIDDLE_BUTTON_DOWN, self._on_middle_button_down)
        self._canvas.bind(tk_events.MIDDLE_BUTTON_UP, self._on_middle_button_up)
        self._canvas.bind(tk_events.MOUSE_MOTION, self._on_mouse_motion)
        self._canvas.bind(
            tk_events.MOUSE_MOTION_WHILE_LEFT_BUTTON_DOWN,
            self._on_motion_while_left_button_down,
        )
        self._canvas.bind(tk_events.MOUSE_ENTERS_WIDGET, self._on_mouse_enters_canvas)
        self._canvas.bind(tk_events.MOUSE_LEAVES_WIDGET, self._on_mouse_leaves_canvas)
        self._canvas.bind(tk_events.MOUSE_WHEEL_SCROLLED, self._on_mouse_wheel_scrolled)
        self._canvas.bind(tk_events.PLUS_KEY, self._on_plus)
        self._canvas.bind(tk_events.KEYPAD_PLUS_KEY, self._on_plus)
        self._canvas.bind(tk_events.LEFT_ARROW_KEY, self._on_left_key)
        self._canvas.bind(tk_events.RIGHT_ARROW_KEY, self._on_right_key)
        self._canvas.bind(tk_events.RETURN_KEY, self._on_return_key)
        self._canvas.bind(tk_events.KEYPAD_RETURN_KEY, self._on_return_key)
        self._canvas.bind(tk_events.DELETE_KEY, self._on_delete_keys)
        self._canvas.bind(tk_events.BACKSPACE_KEY, self._on_delete_keys)
        self._canvas.bind(tk_events.ESCAPE_KEY, self._on_escape_key)
        self._canvas.bind(tk_events.ALPHANUMERIC_KEY, self._on_alphanumeric_key)
        self._canvas.bind(tk_events.CONTROL_RIGHT, self._on_control_right_key)

    def _on_left_button_down(self, event: Any) -> None:
        pass

    def _on_left_button_up(self, event: Any) -> None:
        x, y = self._get_mouse_coordinates(event)
        self._presenter.try_add_event(x=x, y=y)

    def _on_right_button_up(self, event: Any) -> None:
        self._presenter.finsh_active_count()

    def _on_middle_button_down(self, event: Any) -> None:
        self._middle_button_pressed = True

    def _on_middle_button_up(self, event: Any) -> None:
        self._middle_button_pressed = False

    def _on_mouse_motion(self, event: Any) -> None:
        pass

    def _on_motion_while_left_button_down(self, event: Any) -> None:
        pass

    def _on_mouse_leaves_canvas(self, event: Any) -> None:
        pass

    def _on_mouse_enters_canvas(self, event: Any) -> None:
        self._canvas.focus_set()

    def _on_mouse_wheel_scrolled(self, event: Any) -> None:
        scroll_delta = event.delta
        if ON_WINDOWS:
            scroll_delta = scroll_delta / 120

        self._presenter.scroll_through_videos(
            scroll_delta=scroll_delta,
            mouse_wheel_pressed=self._middle_button_pressed,
        )

    def _on_plus(self, event: Any) -> None:
        pass

    def _on_control_right_key(self, event: Any) -> None:
        if self._current_jump_time_step == list(JUMP_TIME_STEPS.keys())[-1]:
            self._current_jump_time_step = list(JUMP_TIME_STEPS.keys())[0]
        else:
            self._current_jump_time_step += 1
        print(
            f"New jump time step: {JUMP_TIME_STEPS[self._current_jump_time_step]} sec"
        )

    def _on_left_key(self, event: Any) -> None:
        delta_of_time = -1 * JUMP_TIME_STEPS[self._current_jump_time_step]
        self._presenter.jump_by_delta_time_in_sec(delta_of_time=delta_of_time)

    def _on_right_key(self, event: Any) -> None:
        delta_of_time = JUMP_TIME_STEPS[self._current_jump_time_step]
        self._presenter.jump_by_delta_time_in_sec(delta_of_time=delta_of_time)

    def _on_return_key(self, event: Any) -> None:
        self._presenter.finsh_active_count()

    def _on_delete_keys(self, event: Any) -> None:
        pass

    def _on_escape_key(self, event: Any) -> None:
        self._presenter.abort_active_count()

    def _on_alphanumeric_key(self, event: Any) -> None:
        key = event.keysym
        self._presenter.set_road_user_class_for_active_count(key)

    def _get_mouse_coordinates(self, event: Any) -> tuple[int, int]:
        """Returns coordinates of event on canvas taking into account the horizontal and
        vertical scroll factors ("xscroll" and "yscroll") in case the canvas is zoomed
        and scrolled.

        Args:
            event (Any): Event on canvas

        Returns:
            tuple[int, int]: Coordinates of the event
        """
        x = int(self._canvas.canvasx(event.x))
        y = int(self._canvas.canvasy(event.y))
        return x, y
