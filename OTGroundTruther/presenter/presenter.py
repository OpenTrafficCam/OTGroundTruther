from pathlib import Path
from tkinter.filedialog import askopenfilename, askopenfilenames, asksaveasfilename

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
        self._gui.frame_treeview.combobox_counts.fill_and_set(
            class_names=self._model._valid_road_user_classes.get_class_names()
        )
        if self._model._video_repository.is_empty():
            return
        self._display_first_frame()
        if self._model._section_repository.is_empty():
            return
        self._refresh_current_frame()
        self.refresh_treeview()

        # TODO: Also refresh when count_repository not empty

    def load_video_files(self) -> None:
        output_askfile = askopenfilenames(
            defaultextension=f"*.{DEFAULT_VIDEO_FILE_SUFFIX}",
            filetypes=[
                ("mp4", f"*.{DEFAULT_VIDEO_FILE_SUFFIX}"),
            ],
        )
        if output_askfile:
            self._model.load_videos_from_files([Path(file) for file in output_askfile])
            self._display_first_frame()

    def _display_first_frame(self) -> None:
        overlayed_first_frame = self._model.get_first_frame(
            selected_classes=self.get_selected_classes_from_gui()
        )
        self._update_canvas_image(overlayed_frame=overlayed_first_frame)

    def load_otflow(self) -> None:
        output_askfile = askopenfilename(
            defaultextension=f"*.{OTANALYTICS_FILE_SUFFIX}",
            filetypes=[
                ("otevents", f"*.{OTANALYTICS_FILE_SUFFIX}"),
            ],
        )
        if output_askfile:
            self._model.read_sections_from_file(Path(output_askfile))
            if self._current_frame is None:
                return
            self._refresh_current_frame()

    def load_events(self) -> None:
        output_askfile = askopenfilename(
            defaultextension=f"*.{GROUND_TRUTH_EVENTS_FILE_SUFFIX}",
            filetypes=[
                ("otgtevents", f"*.{GROUND_TRUTH_EVENTS_FILE_SUFFIX}"),
                ("otevents", f"*.{OTEVENTS_FILE_SUFFIX}"),
            ],
        )
        if output_askfile:
            self._model.read_sections_from_file(Path(output_askfile))
            self._model.read_events_from_file(Path(output_askfile))
            if self._current_frame is None:
                return
            self._refresh_current_frame()

    def save_events(self) -> None:
        first_video_file = (
            self._model._video_repository.get_first_video().get_filepath()
        )
        output_asksave = asksaveasfilename(
            initialdir=first_video_file.parent,
            initialfile=first_video_file.stem,
            defaultextension=GROUND_TRUTH_EVENTS_FILE_SUFFIX,
            filetypes=[("OTGTEvent file", GROUND_TRUTH_EVENTS_FILE_SUFFIX)],
            title="Save all Events",
        )
        if output_asksave:
            sections = self._model._section_repository.to_list()
            event_list = self._model._count_repository.to_event_list()
            self._model.write_events_and_sections_to_file(
                event_file_path=Path(output_asksave),
                event_list=event_list,
                sections=sections,
            )

    def _refresh_current_frame(self) -> None:
        if self._current_frame is None:
            return
        overlayed_frame = self._model.refresh_current_frame(
            current_frame=self._current_frame,
            selected_classes=self.get_selected_classes_from_gui(),
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
            selected_classes=self.get_selected_classes_from_gui(),
            delta_of_frames=capped_scroll_delta,
            delta_of_time=0,
        )
        self._update_canvas_image(overlayed_frame=overlayed_frame)

    def jump_by_delta_time_in_sec(self, delta_of_time: float) -> None:
        if self._current_frame is not None:
            overlayed_frame = self._model.get_frame_by_delta_frames_or_time(
                current_frame=self._current_frame,
                selected_classes=self.get_selected_classes_from_gui(),
                delta_of_frames=0,
                delta_of_time=delta_of_time,
            )
            self._update_canvas_image(overlayed_frame=overlayed_frame)

    def _update_canvas_image(self, overlayed_frame: OverlayedFrame) -> None:
        self._gui.frame_canvas.canvas_background.update_image(
            image=overlayed_frame.get()
        )
        self._current_frame = overlayed_frame

    def refresh_treeview(self) -> None:
        self._gui.frame_treeview.treeview_counts.refresh_treeview(
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
        self.update_canvas_image_with_new_overlay()

        if not self._model.active_count_class_is_set():
            self._gui.frame_treeview.treeview_counts.selection_set("")
            self._gui.frame_treeview.class_label.set_blank()

    def update_canvas_image_with_new_overlay(self) -> None:
        if self._current_frame is not None:
            overlayed_frame = self._model._get_overlayed_frame(
                background_frame=self._current_frame.background_frame,
                selected_classes=self.get_selected_classes_from_gui(),
            )
            self._update_canvas_image(overlayed_frame=overlayed_frame)

    def set_road_user_class_for_active_count(self, key: str) -> None:
        road_user_class = self._model.set_road_user_class_for_active_count(key)
        if road_user_class is not None:
            self.update_canvas_image_with_new_overlay()
            self._gui.frame_treeview.class_label.show_class_img(
                road_user_class=road_user_class
            )

    def finsh_active_count(self) -> None:
        try:
            count = self._model.add_active_count_to_repository()
        except TooFewEventsError:
            print("Too few events, you need at least two events to finish a count")
        except MissingRoadUserClassError:
            print("Please specify a class for the road user")
        else:
            if count is not None:
                self._gui.frame_treeview.treeview_counts.add_and_select_count_if_in(
                    count=count
                )

        return

    def abort_active_count(self) -> None:
        self._model.clear_active_count()
        self.update_canvas_image_with_new_overlay()
        self._gui.frame_treeview.class_label.set_blank()

    def delete_selected_counts(self) -> None:
        to_delete_count_ids = (
            self._gui.frame_treeview.treeview_counts.delete_selected_count()
        )
        self._model.delete_counts(to_delete_count_ids)
        self._gui.frame_treeview.class_label.set_blank()
        self.update_canvas_image_with_new_overlay()

    def show_start_of_count(self, count_id: int):
        overlayed_frame = self._model.get_start_frame_of_count(
            count_id=count_id, selected_classes=self.get_selected_classes_from_gui()
        )
        self._update_canvas_image(overlayed_frame=overlayed_frame)

    def get_selected_classes_from_gui(self) -> list[str]:
        return self._gui.frame_treeview.combobox_counts.get_selected_classes()

    def show_class_image_by_count_id(self, count_id: int) -> None:
        road_user_class = self._model._count_repository.get_all_as_dict()[
            count_id
        ].get_road_user_class()
        self._gui.frame_treeview.class_label.show_class_img(
            road_user_class=road_user_class
        )
