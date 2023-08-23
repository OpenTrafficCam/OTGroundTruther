import datetime as dt
from pathlib import Path

import numpy as np

from .coordinate import Coordinate
from .count import ActiveCount, Count
from .datastore import Datastore
from .event import Event
from .section import LineSection, SectionParser
from .video import NoVideoError, Video


class OTGroundTrutherApplication:
    """
    Entrypoint for calls from the UI.
    """

    def __init__(
        self,
        datastore: Datastore,
        active_count: ActiveCount | None = None,
        video: Video | None = None,
    ) -> None:
        self._datastore: Datastore = datastore
        self._video = video
        self._active_count = active_count
        self._section_parser: SectionParser = SectionParser

    def read_sections_from_file(self, file: Path) -> None:
        self._datastore.section_repository.clear()
        sections, otanalytics_file_content = self._section_parser.parse(file=file)
        self._datastore.section_repository.add_all(sections)
        self._datastore.section_repository.set_otanalytics_file_content(
            otanalytics_file_content
        )

    def read_events_from_file(self, file: Path) -> None:
        pass

    def write_events_to_file(self, file: Path) -> None:
        pass

    def get_section_by_coordinate(self, coordinate: Coordinate) -> LineSection | None:
        return self._datastore.section_repository.get_by_coordinate(coordinate)

    def load_video_from_file(self, file: Path):
        del self._video
        self._video = Video(file)

    def get_video_frame(self) -> np.array:
        if self._video is None:
            raise NoVideoError
        self._video.get_frame()

    def set_video_frame(self, frame_number: int) -> None:
        if self._video is None:
            raise NoVideoError
        self._video.set_frame_number(frame_number)

    def get_event_for(self, coordinate: Coordinate) -> Event | None:
        section = self.get_section_by_coordinate(coordinate)
        if section is None:
            return
        if self._video is None:
            raise NoVideoError
        frame = self._video.get_frame_number()
        timestamp = self._video.get_timestamp()
        video = self._video.file
        created = dt.datetime.now().timestamp()
        return Event(
            coordinate,
            section,
            frame=frame,
            timestamp=timestamp,
            video=video,
            time_created=created,
        )

    def add_event_to_active_count(self, event: Event) -> None:
        if self._active_count is None:
            self._active_count = ActiveCount(event)
        else:
            self._active_count.add_event(event)

    def add_active_count_to_counts(self, count: Count, road_user_class: str) -> None:
        if self._active_count is None:
            return
        _id = self._datastore.count_repository.get_id()
        count = Count(
            id=_id,
            events=self._active_count.get_events(),
            road_user_class=road_user_class,
        )
        self._datastore.count_repository.add(count)
        self._active_count = None

    def get_all_counts(self) -> list[Count]:
        self._datastore.count_repository.get_all()

    def delete_count(self, id: str) -> None:
        self._datastore.count_repository.remove(id)

    def get_counts_by_frame(self, frame: int) -> list[Count]:
        self._datastore.count_repository.get_by_frame_of_events(frame)
