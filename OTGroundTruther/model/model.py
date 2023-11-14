import datetime as dt
from pathlib import Path

from OTGroundTruther.gui.constants import tk_events
from OTGroundTruther.gui.key_assignment import (
    KEY_ASSIGNMENT_ACTIONS,
    KEY_ASSIGNMENT_KEYS,
)
from OTGroundTruther.model.coordinate import Coordinate
from OTGroundTruther.model.count import (
    ActiveCount,
    Count,
    CountRepository,
    CountsOverlay,
    MissingRoadUserClassError,
)
from OTGroundTruther.model.event import (
    Event,
    EventForParsingSerializing,
    EventListParser,
)
from OTGroundTruther.model.overlayed_frame import OverlayedFrame
from OTGroundTruther.model.road_user_class import RoadUserClass, ValidRoadUserClasses
from OTGroundTruther.model.section import (
    LineSection,
    SectionParser,
    SectionRepository,
    SectionsOverlay,
)
from OTGroundTruther.model.video import (
    BackgroundFrame,
    NoVideoError,
    TimestampNotFoundInVideosError,
    Video,
    VideoRepository,
)


class Model:
    """
    Entrypoint for calls from the UI.
    """

    def __init__(
        self,
        video_repository: VideoRepository,
        section_repository: SectionRepository,
        count_repository: CountRepository,
        active_count: ActiveCount | None,
        valid_road_user_classes: ValidRoadUserClasses,
    ) -> None:
        self._video_repository = video_repository
        self._section_repository = section_repository
        self._count_repository = count_repository
        self._active_count = active_count
        self._valid_road_user_classes = valid_road_user_classes
        self._section_parser: SectionParser = SectionParser()
        self._eventlistparser: EventListParser = EventListParser()

    def load_videos_from_files(self, files: list[Path]):
        self._video_repository.clear()
        videos = [Video(file) for file in files]
        self._video_repository.add_all(videos)
        print(f"Videos loaded: {files}")

    def read_sections_from_file(self, file: Path) -> None:
        self._section_repository.clear()
        sections, otanalytics_file_content = self._section_parser.parse(file=file)
        self._section_repository.add_all(sections)
        self._section_repository.set_otanalytics_file_content(otanalytics_file_content)
        print(f"Sections read from {file}")

    def read_events_from_file(self, file: Path) -> None:
        event_list = self._eventlistparser.parse(
            otevent_file=file,
            sections=self._section_repository.to_dict(),
            valid_road_user_classes=self._valid_road_user_classes,
        )
        self._count_repository.from_event_list(event_list)
        print(f"Events read from {file}")

    def write_events_and_sections_to_file(
        self,
        event_file_path: Path,
        event_list: list[EventForParsingSerializing],
        sections: list[LineSection],
    ) -> None:
        self._eventlistparser.serialize(
            events=event_list,
            sections=sections,
            file=event_file_path,
        )
        print(f"Events written to {str(event_file_path)}")

    def get_frame_by_timestamp(
        self, unix_timestamp: float, selected_classes: list[str]
    ) -> OverlayedFrame:
        if self._video_repository == []:
            raise NoVideoError
        video = self._video_repository.get_by_timestamp(unix_timestamp)
        if video is None:
            raise TimestampNotFoundInVideosError
        background_frame = video.get_frame_by_timestamp(unix_timestamp)
        return self._get_overlayed_frame(
            background_frame=background_frame, selected_classes=selected_classes
        )

    def get_frame_by_delta_frames_or_time(
        self,
        current_frame: OverlayedFrame,
        selected_classes: list[str],
        delta_of_frames: int = 0,
        delta_of_time: float = 0,
    ) -> OverlayedFrame:
        (
            video,
            frame_number,
        ) = self._video_repository.get_video_and_frame_by_delta_frame_or_time(
            current_file_name=current_frame.background_frame.get_video_name(),
            current_frame_number=current_frame.background_frame.frame_number,
            delta_of_frames=delta_of_frames,
            delta_of_time=delta_of_time,
        )
        background_frame = video.get_frame_by_number(frame_number)
        return self._get_overlayed_frame(
            background_frame=background_frame, selected_classes=selected_classes
        )

    def get_first_frame(self, selected_classes: list[str]) -> OverlayedFrame:
        first_video = self._video_repository.get_first_video()
        background_frame = first_video.get_frame_by_number(0)
        return self._get_overlayed_frame(
            background_frame=background_frame, selected_classes=selected_classes
        )

    def refresh_current_frame(
        self, current_frame: OverlayedFrame, selected_classes: list[str]
    ) -> OverlayedFrame:
        current_video = self._video_repository.get_video_by_name(
            current_frame.background_frame.get_video_name()
        )
        background_frame = current_video.get_frame_by_number(
            current_frame.background_frame.frame_number
        )
        return self._get_overlayed_frame(
            background_frame=background_frame, selected_classes=selected_classes
        )

    def _get_overlayed_frame(
        self, background_frame: BackgroundFrame, selected_classes: list[str]
    ) -> OverlayedFrame:
        sections_overlay = SectionsOverlay(
            sections=self._section_repository.to_list(),
            width=background_frame.get_width(),
            height=background_frame.get_height(),
        )
        counts_overlay = CountsOverlay(
            background_frame=background_frame,
            count_repository=self._count_repository,
            active_count=self._active_count,
            selected_classes=selected_classes,
        )
        return OverlayedFrame(
            background_frame=background_frame,
            sections_overlay=sections_overlay,
            counts_overlay=counts_overlay,
        )

    def get_event_for(
        self, coordinate: Coordinate, current_frame: OverlayedFrame | None
    ) -> Event | None:
        if current_frame is None:
            return None
        section = self.get_section_by_coordinate(coordinate)
        if section is None:
            return None
        now = dt.datetime.now().timestamp()
        return Event(
            coordinate,
            section,
            frame_number=current_frame.background_frame.frame_number,
            timestamp=current_frame.background_frame.unix_timestamp,
            video_file_name=current_frame.background_frame.video_file.stem,
            time_created=now,
        )

    def get_section_by_coordinate(self, coordinate: Coordinate) -> LineSection | None:
        return self._section_repository.get_by_coordinate(coordinate)

    def add_event_to_active_count(self, event: Event) -> None:
        if self._active_count is None:
            self._active_count = ActiveCount(event)
            print("New active count")
        else:
            self._active_count.add_event(event)
        print(f"New event: {event.to_dict()}")

    def set_road_user_class_for_active_count(self, key: str) -> RoadUserClass | None:
        if self._active_count is None:
            return None
        road_user_class = self._valid_road_user_classes.get_by_key(key)
        if road_user_class is None:
            return None
        self._active_count.set_road_user_class(road_user_class)
        print(f"Road user class: {road_user_class.get_name()}")
        return road_user_class

    def add_active_count_to_repository(self) -> Count | None:
        if self._active_count is None:
            return None
        _id = self._count_repository.get_id()
        road_user_class = self._active_count.get_road_user_class()
        if road_user_class is None:
            raise MissingRoadUserClassError
        count = Count(
            road_user_id=_id,
            events=self._active_count.get_events(),
            road_user_class=road_user_class,
        )
        self._count_repository.add(count)
        self._active_count = None
        print("Active count finished")
        return count

    def active_count_class_is_set(self) -> bool:
        if (
            self._active_count is None
            or self._active_count.get_road_user_class() is None
        ):
            return False
        else:
            return True

    def clear_active_count(self) -> None:
        self._active_count = None
        print("Active count aborted")

    def get_all_counts(self) -> list[Count]:
        return self._count_repository.get_all_as_list()

    def delete_count(self, id: int) -> None:
        self._count_repository.delete(id=id)

    def delete_counts(self, ids: list[int]) -> None:
        for id in ids:
            self.delete_count(id=id)

    def get_counts_by_frame(self, frame_number: int) -> list[Count]:
        return self._count_repository.get_by_frame_of_events(frame_number)

    def clear_repositories(self) -> None:
        self._section_repository.clear()
        self._count_repository.clear()
        self._video_repository.clear()
        self.active_count = None

    def get_start_frame_of_last_count(
        self, selected_classes: list[str]
    ) -> OverlayedFrame:
        last_added_count = list(self._count_repository.get_all_as_dict().values())[-1]
        event = last_added_count.get_first_event()
        return self.get_frame_by_event(event=event, selected_classes=selected_classes)

    def get_frame_by_event(
        self, event: Event, selected_classes: list[str]
    ) -> OverlayedFrame:
        video = self._video_repository.get_video_by_name(event.get_video_file_name())
        background_frame = video.get_frame_by_number(event.get_frame_number())
        return self._get_overlayed_frame(
            background_frame=background_frame, selected_classes=selected_classes
        )

    def get_start_frame_of_count(self, count_id: int, selected_classes: list[str]):
        event = self._count_repository.get_all_as_dict()[count_id].get_first_event()
        return self.get_frame_by_event(event=event, selected_classes=selected_classes)

    def get_key_assignment_text(self) -> dict[str, str]:
        key_assignment_lists = {
            KEY_ASSIGNMENT_ACTIONS: ["General", ""],
            KEY_ASSIGNMENT_KEYS: ["", ""],
        }
        for button_name, action in tk_events.key_assignment.items():
            if action != "":
                key_assignment_lists[KEY_ASSIGNMENT_ACTIONS].append(f"{action}   -")
                key_assignment_lists[KEY_ASSIGNMENT_KEYS].append(f"{button_name[1:-1]}")
        key_assignment_lists[KEY_ASSIGNMENT_ACTIONS] += ["", "", "Class assignment", ""]
        key_assignment_lists[KEY_ASSIGNMENT_KEYS] += ["", "", "", ""]
        for (
            key,
            class_name,
        ) in self._valid_road_user_classes.to_dict_key_with_name().items():
            key_assignment_lists[KEY_ASSIGNMENT_ACTIONS].append(f"{class_name}   -")
            key_assignment_lists[KEY_ASSIGNMENT_KEYS].append(f"{key}")
        key_assignment_lists[KEY_ASSIGNMENT_ACTIONS] = [
            string + "\n" for string in key_assignment_lists[KEY_ASSIGNMENT_ACTIONS]
        ]
        key_assignment_lists[KEY_ASSIGNMENT_KEYS] = [
            string + "\n" for string in key_assignment_lists[KEY_ASSIGNMENT_KEYS]
        ]
        key_assignment_text = {}
        key_assignment_text[KEY_ASSIGNMENT_ACTIONS] = "".join(
            key_assignment_lists[KEY_ASSIGNMENT_ACTIONS]
        )
        key_assignment_text[KEY_ASSIGNMENT_KEYS] = "".join(
            key_assignment_lists[KEY_ASSIGNMENT_KEYS]
        )

        return key_assignment_text
