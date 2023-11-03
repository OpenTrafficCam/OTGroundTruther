from pathlib import Path
from tkinter.filedialog import askopenfilename, askopenfilenames

from OTGroundTruther.gui.gui import Gui
from OTGroundTruther.gui.presenter_interface import PresenterInterface
from OTGroundTruther.model.config import (
    DEFAULT_VIDEO_FILE_SUFFIX,
    GROUND_TRUTH_EVENTS_FILE_SUFFIX,
    OTANALYTICS_FILE_SUFFIX,
    OTEVENTS_FILE_SUFFIX,
)
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

    def after_run_gui(self) -> None:
        if self._model._video_repository.is_empty():
            return
        self._display_first_frame()
        if self._model._section_repository.is_empty():
            return
        self._refresh_current_frame()

        # TODO: Also refresh when count_repository not empty

    def load_video_files(self) -> None:
        video_files = askopenfilenames(
            defaultextension=f"*.{DEFAULT_VIDEO_FILE_SUFFIX}",
            filetypes=[
                ("mp4", f"*.{DEFAULT_VIDEO_FILE_SUFFIX}"),
            ],
        )
        self._model.load_videos_from_files([Path(file) for file in video_files])
        self._display_first_frame()

    def _display_first_frame(self) -> None:
        overlayed_first_frame = self._model.get_first_frame()
        self._update_canvas_image(overlayed_frame=overlayed_first_frame)

    def load_otflow(self) -> None:
        otflow_file = askopenfilename(
            defaultextension=f"*.{OTANALYTICS_FILE_SUFFIX}",
            filetypes=[
                ("otevents", f"*.{OTANALYTICS_FILE_SUFFIX}"),
            ],
        )
        self._model.read_sections_from_file(Path(otflow_file))
        if self._current_frame is None:
            return
        self._refresh_current_frame()

    def load_events(self) -> None:
        events_file = askopenfilename(
            defaultextension=f"*.{GROUND_TRUTH_EVENTS_FILE_SUFFIX}",
            filetypes=[
                ("otgtevents", f"*.{GROUND_TRUTH_EVENTS_FILE_SUFFIX}"),
                ("otevents", f"*.{OTEVENTS_FILE_SUFFIX}"),
            ],
        )
        self._model.read_sections_from_file(Path(events_file))
        self._model.read_events_from_file(Path(events_file))
        if self._current_frame is None:
            return
        self._refresh_current_frame()
        self.update_treeview()

    def save_events(self) -> None:
        sections = self._model._section_repository.to_list()
        event_list = self._model._count_repository.to_event_list()
        self._model.write_events_and_sections_to_file(
            event_list, sections, GROUND_TRUTH_EVENTS_FILE_SUFFIX
        )

    def _refresh_current_frame(self) -> None:
        if self._current_frame is None:
            return
        overlayed_frame = self._model.refresh_current_frame(
            current_frame=self._current_frame
        )
        self._update_canvas_image(overlayed_frame=overlayed_frame)

    def scroll_through_videos(
        self, scroll_delta: int, mouse_wheel_pressed: bool
    ) -> None:
        if self._current_frame is None:
            return
        if scroll_delta < 0:
            capped_scroll_delta = max(scroll_delta, -MAX_SCROLL_STEP)
        else:
            capped_scroll_delta = min(scroll_delta, MAX_SCROLL_STEP)
        overlayed_frame = self._model.get_frame_by_delta_frames_or_time(
            current_frame=self._current_frame,
            delta_of_frames=capped_scroll_delta,
            delta_of_time=0,
        )
        self._update_canvas_image(overlayed_frame=overlayed_frame)

    def jump_by_delta_time_in_sec(self, delta_of_time: float) -> None:
        if self._current_frame is not None:
            overlayed_frame = self._model.get_frame_by_delta_frames_or_time(
                current_frame=self._current_frame,
                delta_of_frames=0,
                delta_of_time=delta_of_time,
            )
            self._update_canvas_image(overlayed_frame=overlayed_frame)

    def _update_canvas_image(self, overlayed_frame: OverlayedFrame) -> None:
        self._gui.frame_canvas.canvas_background.update_image(
            image=overlayed_frame.get()
        )
        self._current_frame = overlayed_frame

    def update_treeview(self):
        self._gui.frame_treeview.treeview_count.update_treeview(
            count_repository=self._model._count_repository
        )

    def try_add_event(self, x: int, y: int) -> None:
        coordinate = Coordinate(x, y)
        event = self._model.get_event_for(
            coordinate=coordinate, current_frame=self._current_frame
        )
        if event is None:
            return
        self._model.add_event_to_active_count(event)
        self._update_canvas_image_with_new_overlay()

    def _update_canvas_image_with_new_overlay(self):
        if self._current_frame is not None:
            overlayed_frame = self._model._get_overlayed_frame(
                background_frame=self._current_frame.background_frame
            )
            self._update_canvas_image(overlayed_frame=overlayed_frame)

    def set_road_user_class_for_active_count(self, key: str) -> None:
        self._model.set_road_user_class_for_active_count(key)

        self._update_canvas_image_with_new_overlay()

    def finsh_active_count(self) -> None:
        try:
            self._model.add_active_count_to_repository()
        except TooFewEventsError:
            print("Too few events, you need at least two events to finish a count")
        except MissingRoadUserClassError:
            print("Please specify a class for the road user")
        else:
            overlayed_frame = self._model.get_startframe_of_last_count()
            self._update_canvas_image(overlayed_frame=overlayed_frame)
        return

    def abort_active_count(self) -> None:
        self._model.clear_active_count()
        self._update_canvas_image_with_new_overlay()
