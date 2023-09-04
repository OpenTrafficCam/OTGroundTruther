from pathlib import Path
from tkinter.filedialog import askopenfilename, askopenfilenames

from OTGroundTruther.gui.gui import Gui
from OTGroundTruther.gui.presenter_interface import PresenterInterface
from OTGroundTruther.model.coordinate import Coordinate
from OTGroundTruther.model.count import MissingRoadUserClassError, TooFewEventsError
from OTGroundTruther.model.model import Model
from OTGroundTruther.model.overlayed_frame import OverlayedFrame

MAX_SCROLL_STEP: int = 50


class Presenter(PresenterInterface):
    def __init__(self, model: Model) -> None:
        self._model = model
        self._gui = Gui(presenter=self)
        self._current_frame: OverlayedFrame | None = None

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
        self._refresh_current_frame()

    def load_otevents(self) -> None:
        otevent_file = askopenfilename(defaultextension="*.otevents")
        self._model.read_events_from_file(Path(otevent_file))
        if self._current_frame is None:
            return
        self._refresh_current_frame()
    
    def save_otevents(self) -> None:
        event_list = self._model._count_repository.to_event_list()
        self._model.write_events_to_file(event_list)

    def _refresh_current_frame(self) -> None:
        frame = self._model.get_current_frame(current_frame=self._current_frame)
        self._update_canvas_image(frame=frame)

    def scroll_through_videos(
        self, scroll_delta: int, mouse_wheel_pressed: bool
    ) -> None:
        if self._current_frame is None:
            return
        if scroll_delta < 0:
            capped_scroll_delta = max(scroll_delta, -MAX_SCROLL_STEP)
        else:
            capped_scroll_delta = min(scroll_delta, MAX_SCROLL_STEP)
        frame = self._model.get_frame_by_delta_of_frames(
            current_frame=self._current_frame, delta_of_frames=capped_scroll_delta
        )
        self._update_canvas_image(frame)

    def _update_canvas_image(self, frame: OverlayedFrame) -> None:
        self._gui.frame_canvas.canvas_background.update_image(image=frame.get())
        self._current_frame = frame

    def try_add_event(self, x: int, y: int) -> None:
        coordinate = Coordinate(x, y)
        event = self._model.get_event_for(
            coordinate=coordinate, current_frame=self._current_frame
        )
        if event is None:
            return
        self._model.add_event_to_active_count(event)

    def set_road_user_class_for_active_count(self, key: str) -> None:
        self._model.set_road_user_class_for_active_count(key)

    def finsh_active_count(self) -> None:
        try:
            self._model.add_active_count_to_repository()
        except TooFewEventsError:
            print("Too few events, you need at least two events to finish a count")
        except MissingRoadUserClassError:
            print("Please specify a class for the road user")
        finally:
            return

    def abort_active_count(self) -> None:
        self._model.clear_active_count()
