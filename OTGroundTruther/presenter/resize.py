from OTGroundTruther.gui.gui import Gui
from OTGroundTruther.model.model import Model


class ResizeFactorCanvas:
    def __init__(self, gui: Gui, model: Model):
        self._gui = gui
        self._model = model

    def get_x(self) -> float:
        video_width = self._get_video_width()
        return 1 if video_width is None else self._get_canvas_width / video_width

    def get_y(self) -> float:
        video_height = self._get_video_height()
        return 1 if video_height is None else self._get_canvas_height / video_height

    def _get_canvas_width(self) -> int:
        return self._gui.frame_canvas.canvas_background._get_width()

    def _get_canvas_height(self) -> int:
        return self._gui.frame_canvas.canvas_background._get_height()

    def _get_video_width(self) -> int | None:
        return None if self._model._video is None else self._model._video.get_width()

    def _get_video_height(self) -> int | None:
        return None if self._model._video is None else self._model._video.get_height()


class CoordinateConverter:
    def __init__(self, resize_factor_cvanvas: ResizeFactorCanvas):
        self._resize_factor_canvas = resize_factor_cvanvas

    def to_video(self, canvas_coordinate: tuple[int, int]) -> tuple[int, int]:
        x_canvas, y_canvas = canvas_coordinate
        x_video = x_canvas / self._resize_factor_canvas.get_x()
        y_video = y_canvas / self._resize_factor_canvas.get_y()
        return x_video, y_video

    def to_canvas(self, video_coordinate: tuple[int, int]) -> tuple[int, int]:
        x_video, y_video = video_coordinate
        x_canvas = int(round(x_video * self._resize_factor_canvas.get_x()))
        y_canvas = int(round(y_video * self._resize_factor_canvas.get_y()))
        return x_canvas, y_canvas
