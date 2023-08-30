from pathlib import Path
from tkinter.filedialog import askopenfilename, askopenfilenames

from OTGroundTruther.gui.gui import Gui
from OTGroundTruther.gui.presenter_interface import PresenterInterface

# from OTGroundTruther.model.coordinate import Coordinate
from OTGroundTruther.model.model import Model
from OTGroundTruther.model.video import BackgroundFrame
from OTGroundTruther.presenter.state import DisplayedFrameState

SCROLL_STEP_SECONDS: float = 0.05
MAX_SCROLL_STEP: int = 50


class Presenter(PresenterInterface):
    def __init__(self, model: Model) -> None:
        self._model = model
        self._gui = Gui(presenter=self)
        self._displayed_frame_state: DisplayedFrameState = DisplayedFrameState(
            None, None
        )
        self._current_frame: BackgroundFrame | None = None

    def run_gui(self) -> None:
        self._gui.run()

    def load_video_files(self) -> None:
        video_files = askopenfilenames(defaultextension="*.mp4")
        self._model.load_videos_from_files([Path(file) for file in video_files])
        self._display_first_frame()

    def _display_first_frame(self) -> None:
        first_frame = self._model.get_first_frame()
        self._update_canvas_image(first_frame)

    def load_otflow(self) -> None:
        otflow_file = askopenfilename(defaultextension="*.otlfow")
        self._model.read_sections_from_file(Path(otflow_file))
        if self._current_frame is None:
            return
        # TODO: Redraw frame with sections

    def scroll_through_videos(
        self, scroll_delta: int, mouse_wheel_pressed: bool
    ) -> None:
        if self._current_frame is None:
            return
        if scroll_delta < 0:
            capped_scroll_delta = max(scroll_delta, -MAX_SCROLL_STEP)
        else:
            capped_scroll_delta = min(scroll_delta, MAX_SCROLL_STEP)
        print(f"scroll delta: {scroll_delta}")
        print(f"mouse wheel pressed: {mouse_wheel_pressed}")
        frame = self._model.get_frame_by_delta_of_frames(
            current_frame=self._current_frame, delta_of_frames=capped_scroll_delta
        )
        self._update_canvas_image(frame)

    def _display_frame_by_timestamp(self, unix_timestamp) -> None:
        frame = self._model.get_frame_by_timestamp(unix_timestamp)
        self._update_canvas_image(frame)

    def _update_canvas_image(self, frame: BackgroundFrame) -> None:
        self._gui.frame_canvas.canvas_background.update_image(image=frame.get())
        self._current_frame = frame

    def _display_next_frame_by_time_delta(self, time_delta: float):
        pass

    def open_section_files(self) -> None:
        pass

    def open_next_frame(self) -> None:
        pass

    def update_canvas(self) -> None:
        pass

    # def add_event(self, x: int, y: int) -> None:
    #     coordinate = Coordinate(x, y)
    #     event = self._model.get_event_for(coordinate)
    #     if event is None:
    #         return
    #     self._model.add_event_to_active_count(event)
