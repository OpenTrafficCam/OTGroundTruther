import datetime as dt
from pathlib import Path

from OTGroundTruther.model.coordinate import Coordinate
from OTGroundTruther.model.count import ActiveCount, Count, CountRepository
from OTGroundTruther.model.event import Event
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
        pass  # TODO

    def write_events_to_file(self, file: Path) -> None:
        pass  # TODO

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
        self, coordinate: Coordinate, video_file: Path, frame_number: int
    ) -> Event | None:
        section = self.get_section_by_coordinate(coordinate)
        if section is None:
            return
        video = self._video_repository.get_video_by_file(video_file)
        timestamp = video.get_timestamp_by_frame_number(frame_number)
        created = dt.datetime.now().timestamp()
        return Event(
            coordinate,
            section,
            frame=frame_number,
            timestamp=timestamp,
            video=video,
            time_created=created,
        )

    def get_section_by_coordinate(self, coordinate: Coordinate) -> LineSection | None:
        return self._section_repository.get_by_coordinate(coordinate)

    def add_event_to_active_count(self, event: Event) -> None:
        if self._active_count is None:
            self._active_count = ActiveCount(event)
        else:
            self._active_count.add_event(event)

    def add_active_count_to_counts(self, count: Count, road_user_class: str) -> None:
        if self._active_count is None:
            return
        _id = self._count_repository.get_id()
        count = Count(
            id=_id,
            events=self._active_count.get_events(),
            road_user_class=road_user_class,
        )
        self._count_repository.add(count)
        self._active_count = None

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
