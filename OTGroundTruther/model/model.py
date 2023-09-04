import datetime as dt
from pathlib import Path

from OTGroundTruther.model.coordinate import Coordinate
from OTGroundTruther.model.count import ActiveCount, Count, CountRepository
from OTGroundTruther.model.event import Event, Event_For_Saving, EventListParser
from OTGroundTruther.model.overlayed_frame import OverlayedFrame
from OTGroundTruther.model.road_user_class import ValidRoadUserClasses
from OTGroundTruther.model.section import (
    LineSection,
    SectionParser,
    SectionRepository,
    SectionsOverlay,
)
from OTGroundTruther.model.video import (
    BackgroundFrame,
    NoVideoError,
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
        self.eventlistparser: EventListParser = EventListParser()

    def load_videos_from_files(self, files: list[Path]):
        self._video_repository.clear()
        videos = [Video(file) for file in files]
        self._video_repository.add_all(videos)

    def read_sections_from_file(self, file: Path) -> None:
        self._section_repository.clear()
        sections, otanalytics_file_content = self._section_parser.parse(file=file)
        self._section_repository.add_all(sections)
        self._section_repository.set_otanalytics_file_content(otanalytics_file_content)

    def read_events_from_file(self, file: Path) -> None:
        event_list = self.eventlistparser.parse(file)
        self._count_repository.from_event_list(event_list)

    def write_events_to_file(self, event_list: list[Event_For_Saving]) -> None:
        file_parent = self._get_first_videopath_parent()
        file_name = self._get_first_videopath_stem()
        suffix = ".otevents"
        filepath = Path(f"{file_parent}\\{file_name}{suffix}")
        self.eventlistparser.serialize(events=event_list,
                                       sections=self._section_repository._sections,
                                       file=filepath)

    def _get_first_videopath_stem(self):
        return list(self._video_repository._videos.keys())[0].stem

    def _get_first_videopath_parent(self):
        return str(list(self._video_repository._videos.keys())[0].parent)

    def get_frame_by_timestamp(self, unix_timestamp) -> OverlayedFrame:
        if self._video_repository == []:
            raise NoVideoError
        video = self._video_repository.get_by_timestamp(unix_timestamp)
        background_frame = video.get_frame_by_timestamp(unix_timestamp)
        return self._get_overlayed_frame(background_frame)

    def get_frame_by_delta_of_frames(
        self, current_frame: OverlayedFrame, delta_of_frames: int
    ) -> OverlayedFrame:
        video: Video
        frame_number: int
        (
            video,
            frame_number,
        ) = self._video_repository.get_video_and_frame_by_delta_of_frames(
            current_file=current_frame.background_frame.video_file,
            current_frame_number=current_frame.background_frame.frame_number,
            delta_of_frames=delta_of_frames,
        )
        background_frame = video.get_frame_by_number(frame_number)
        return self._get_overlayed_frame(background_frame)

    def get_first_frame(self) -> OverlayedFrame:
        first_video = self._video_repository.get_first()
        background_frame = first_video.get_frame_by_number(0)
        return self._get_overlayed_frame(background_frame)

    def get_current_frame(self, current_frame: OverlayedFrame) -> OverlayedFrame:
        current_video = self._video_repository.get_video_by_file(
            current_frame.background_frame.video_file
        )
        background_frame = current_video.get_frame_by_number(
            current_frame.background_frame.frame_number
        )
        return self._get_overlayed_frame(background_frame)

    def _get_overlayed_frame(self, background_frame: BackgroundFrame) -> OverlayedFrame:
        sections_overlay = SectionsOverlay(
            sections=self._section_repository.get_all(),
            width=background_frame.get_width(),
            height=background_frame.get_height(),
        )
        return OverlayedFrame(
            background_frame=background_frame, sections_overlay=sections_overlay
        )

    def set_video_frame(self, frame_number: int) -> None:
        if self._video is None:
            raise NoVideoError
        self._video.set_frame_number(frame_number)

    def get_event_for(
        self, coordinate: Coordinate, current_frame: OverlayedFrame
    ) -> Event | None:
        section = self.get_section_by_coordinate(coordinate)
        if section is None:
            return
        now = dt.datetime.now().timestamp()
        return Event(
            coordinate,
            section,
            frame_number=current_frame.background_frame.frame_number,
            timestamp=current_frame.background_frame.unix_timestamp,
            video_file=current_frame.background_frame.video_file,
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

    def set_road_user_class_for_active_count(self, key: str):
        road_user_class = self._valid_road_user_classes.get_by_key(key)
        if road_user_class is None:
            return
        if self._active_count is None:
            self._active_count = ActiveCount(road_user_class)
            print("New active count")
        self._active_count.set_road_user_class(road_user_class)
        print(f"Road user class: {road_user_class.label}")

    def add_active_count_to_repository(self) -> None:
        if self._active_count is None:
            return
        _id = self._count_repository.get_id()
        count = Count(
            id=_id,
            events=self._active_count.get_events(),
            road_user_class=self._active_count.get_road_user_class(),
        )
        self._count_repository.add(count)
        self._active_count = None
        print("Active count finished")

    def clear_active_count(self) -> None:
        self._active_count = None
        print("Active count aborted")

    def get_all_counts(self) -> list[Count]:
        self._count_repository.get_all()

    def delete_count(self, id: str) -> None:
        self._count_repository.remove(id)

    def get_counts_by_frame(self, frame: int) -> list[Count]:
        self._count_repository.get_by_frame_of_events(frame)

    def clear_repositories(self) -> None:
        self._section_repository.clear()
        self._count_repository.clear()
        self._video_repository.clear()
        self.active_count = None



