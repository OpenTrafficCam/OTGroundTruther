from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from OTGroundTruther.model.config import (
    DEFAULT_VIDEO_FILE_SUFFIX,
    GROUND_TRUTH_EVENTS_FILE_SUFFIX,
    OTEVENTS_FILE_SUFFIX,
)
from OTGroundTruther.model.coordinate import Coordinate
from OTGroundTruther.model.road_user_class import ValidRoadUserClasses
from OTGroundTruther.model.section import LineSection

from .parse import parse, write_bz2
from .road_user_class import RoadUserClass

METADATA: str = "metadata"
VERSION: str = "version"
SECTION_FORMAT_VERSION: str = "section_file_version"
EVENT_FORMAT_VERSION: str = "event_file_version"
EVENT_LIST = "event_list"
SECTIONS: str = "sections"
SECTION_ID: str = "section_id"
SECTION_NAME: str = "section_name"
EVENT_COORDINATE: str = "event_coordinate"
EVENT_TYPE: str = "event_type"
DIRECTION_VECTOR: str = "direction_vector"
VIDEO_NAME: str = "video_name"
OCCURENCE: str = "occurrence"
HOSTNAME: str = "hostname"

ROAD_USER_CLASS: str = "road_user_class"
ROAD_USER_CLASS_OTEVENTS: str = "road_user_type"
ROAD_USER_ID: str = "road_user_id"
FRAME_NUMBER: str = "frame_number"
TIME_CREATED: str = "time_created"
DATETIME_FORMAT: str = "%Y-%m-%d %H:%M:%S.%f"

SECTION_ENTER: str = "section-enter"

MAX_NUMBER_OF_EVENTS: int = 1000000
MAX_NUMBER_OF_EVENTS_APPLIED: bool = False


class InvalidEventsFileType(Exception):
    pass


class TooManyEvents(Exception):
    pass


@dataclass
class Event:
    coordinate: Coordinate
    section: LineSection
    frame_number: int
    timestamp: float
    video_file_name: str
    time_created: float | None
    event_type: str = SECTION_ENTER

    def to_event_for_serializing(
        self, road_user_id: str, road_user_class: RoadUserClass
    ) -> "EventForParsingSerializing":
        event: dict = vars(self)
        event[ROAD_USER_ID] = road_user_id
        event[ROAD_USER_CLASS] = road_user_class
        return EventForParsingSerializing(**event)

    def to_dict(self) -> dict:
        return {
            EVENT_COORDINATE: self.coordinate.as_list(),
            SECTION_ID: self.section.id,
            SECTION_NAME: self.section.name,
            EVENT_TYPE: self.event_type,
            FRAME_NUMBER: self.frame_number,
            OCCURENCE: self.timestamp,
            VIDEO_NAME: self.video_file_name,
            TIME_CREATED: self.time_created,
        }

    def get_coordinate(self):
        return self.coordinate

    def get_timestamp(self) -> float:
        return self.timestamp

    def get_time_as_str(self) -> str:
        datetime_ = datetime.fromtimestamp(self.timestamp)
        return datetime_.strftime("%Y-%m-%d %H:%M:%S")[5:]

    def get_frame_number(self) -> int:
        return self.frame_number

    def get_video_file_name(self) -> str:
        return self.video_file_name

    def get_section(self) -> LineSection:
        return self.section


@dataclass
class EventForParsingSerializing:
    coordinate: Coordinate
    section: LineSection
    event_type: str
    frame_number: int
    timestamp: float
    video_file_name: str
    time_created: float | None
    road_user_id: str
    road_user_class: RoadUserClass

    def to_event(self) -> Event:
        event_dict = vars(self)
        event_dict.pop(ROAD_USER_ID)
        event_dict.pop(ROAD_USER_CLASS)
        return Event(**event_dict)

    def to_dict(self) -> dict:
        return {
            EVENT_COORDINATE: self.coordinate.as_list(),
            SECTION_ID: self.section.id,
            EVENT_TYPE: self.event_type,
            FRAME_NUMBER: self.frame_number,
            OCCURENCE: self.timestamp,
            VIDEO_NAME: self.video_file_name,
            TIME_CREATED: self.time_created,
            ROAD_USER_ID: self.road_user_id,
            ROAD_USER_CLASS_OTEVENTS: self.road_user_class.get_name(),
            DIRECTION_VECTOR: None,
        }

    def get_road_user_id(self) -> str:
        return self.road_user_id

    def get_road_user_class(self) -> RoadUserClass:
        return self.road_user_class


class EventParser:
    def parse(self, file: Path):
        raise NotImplementedError


class EventListParser:
    def parse(
        self,
        events_file: Path,
        sections: dict[str, LineSection],
        valid_road_user_classes: ValidRoadUserClasses,
    ) -> list[EventForParsingSerializing]:
        """Parse (load) otevents file and convert its content to
        domain level objects namely
        `Events`s.

        Args:
            otevent_file (Path): the file to

        Returns:
            list[Event]: the events.
        """

        if not self._events_file_type_is_supported(events_file):
            raise InvalidEventsFileType

        events_file_content = parse(events_file)
        events: list[dict] = events_file_content[EVENT_LIST]
        if self._exceeds_maximum_events(events):
            raise TooManyEvents

        parsed_events = []
        classes_by_name = valid_road_user_classes.to_dict_with_name_as_key()
        event_type_available = self._event_type_is_available(events)
        enter_events_without_sections: int = 0
        for event in events:
            if event_type_available and not self._is_enter_event(event):
                continue
            if not self._section_of_event_exists(sections, event):
                enter_events_without_sections += 1
                continue

            section = sections[event[SECTION_ID]]
            coordinate = Coordinate(
                round(event[EVENT_COORDINATE][0]),
                round(event[EVENT_COORDINATE][1]),
            )
            road_user_class = classes_by_name[event[ROAD_USER_CLASS_OTEVENTS]]
            video_file_name = self._get_video_file_name(event)
            parsed_events.append(
                EventForParsingSerializing(
                    coordinate=coordinate,
                    section=section,
                    event_type=SECTION_ENTER,
                    frame_number=event[FRAME_NUMBER],
                    timestamp=self._convert_datetime_to_unix(
                        time_input=event[OCCURENCE]
                    ),
                    video_file_name=video_file_name,
                    time_created=event.get(TIME_CREATED, None),
                    road_user_id=str(event[ROAD_USER_ID]),
                    road_user_class=road_user_class,
                )
            )
        if enter_events_without_sections > 0:
            print(
                f"WARNING: No section found for a total of "
                f"{enter_events_without_sections} enter events from {events_file}"
            )
        return parsed_events

    def _exceeds_maximum_events(self, events: list[dict]) -> bool:
        if MAX_NUMBER_OF_EVENTS_APPLIED and len(events) > MAX_NUMBER_OF_EVENTS:
            return True
        return False

    def _get_video_file_name(self, event: dict) -> str:
        video_name = event[VIDEO_NAME]
        if Path(video_name).suffix == "":
            return video_name + DEFAULT_VIDEO_FILE_SUFFIX
        else:
            return video_name

    def _is_from_otanalytics(self, events_file: Path) -> bool:
        if events_file.suffix == OTEVENTS_FILE_SUFFIX:
            return True
        else:
            return False

    def _is_from_otgroundtruther(self, events_file: Path) -> bool:
        if events_file.suffix == GROUND_TRUTH_EVENTS_FILE_SUFFIX:
            return True
        else:
            return False

    def _events_file_type_is_supported(self, events_file: Path) -> bool:
        if self._is_from_otgroundtruther(events_file) or self._is_from_otanalytics(
            events_file
        ):
            return True
        else:
            return False

    def _is_enter_event(self, event: dict) -> bool:
        return event[EVENT_TYPE] == SECTION_ENTER

    def _section_of_event_exists(
        self, sections: dict[str, LineSection], event: dict
    ) -> bool:
        return event[SECTION_ID] in list(sections.keys())

    def _event_type_is_available(self, events: list[dict]):
        if events and EVENT_TYPE in list(events[0].keys()):
            return True
        else:
            return False

    def _convert_datetime_to_unix(self, time_input: float | str) -> float:
        if isinstance(time_input, float):
            return time_input
        else:
            date_object = datetime.strptime(time_input, DATETIME_FORMAT)
            return date_object.timestamp()

    def serialize(
        self,
        events: list[EventForParsingSerializing],
        sections: list[LineSection],
        file: Path,
    ) -> None:
        """Serialize event list into file.

        Args:
            events (Iterable[Event]): events to serialize
            sections (Section): sections to serialize
            file (Path): file to serialize events and sections to
        """
        content = self._convert(events, sections)
        write_bz2(content, file)

    def _convert(
        self,
        events: list[EventForParsingSerializing],
        sections: list[LineSection],
    ) -> dict[str, Any]:
        """Convert events to dictionary.

        Args:
            events (Iterable[Event]): events to convert
            sections (Iterable[Section]): sections to convert

        Returns:
            dict[str, list[dict]]: dictionary containing raw information of events
        """
        metadata = self._build_metadata()
        converted_sections = self._convert_sections(sections)
        converted_events = self._convert_events(events)
        return {
            METADATA: metadata,
            SECTIONS: converted_sections,
            EVENT_LIST: converted_events,
        }

    def _build_metadata(self) -> dict:
        return {
            VERSION: None,
            SECTION_FORMAT_VERSION: None,
            EVENT_FORMAT_VERSION: None,
        }

    def _convert_events(self, events: list[EventForParsingSerializing]) -> list[dict]:
        """Convert events to dictionary.

        Args:
            events (Iterable[Event]): events to convert

        Returns:
            list[dict]: list containing raw information of events
        """
        return [event.to_dict() for event in events]

    def _convert_sections(self, sections: list[LineSection]) -> list[dict]:
        """Convert sections to dictionary

        Args:
            sections (Iterable[Section]): sections to convert

        Returns:
            list[dict]: list containing raw information of sections
        """
        return [section.to_dict() for section in sections]
