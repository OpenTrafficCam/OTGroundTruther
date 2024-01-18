from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

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


class Event:
    def __init__(
        self,
        coordinate: Coordinate,
        section: LineSection,
        frame_number: int,
        timestamp: float,
        video_file_name: str,
        time_created: float | None,
        event_type: str = SECTION_ENTER,
    ) -> None:
        self.coordinate = coordinate
        self.section = section
        self.frame_number = frame_number
        self.timestamp = timestamp
        self.video_file_name = video_file_name
        self.time_created = time_created
        self.event_type = event_type

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
        otevent_file: Path,
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
        otevents_content = parse(otevent_file)
        events: list[dict] = otevents_content[EVENT_LIST]
        if len(events) > MAX_NUMBER_OF_EVENTS:
            events = events[:MAX_NUMBER_OF_EVENTS]
        parsed_events = []
        classes_by_name = valid_road_user_classes.to_dict_with_name_as_key()
        event_type_available = self.is_event_type_is_available(events)
        for event in events:
            if self.event_section_available_and_is_section_entering(
                sections, event_type_available, event
            ):
                section = sections[event[SECTION_ID]]
                coordinate = Coordinate(
                    round(event[EVENT_COORDINATE][0]),
                    round(event[EVENT_COORDINATE][1]),
                )
                road_user_class = classes_by_name[event[ROAD_USER_CLASS_OTEVENTS]]
                if event_type_available:
                    video_file_name = event[VIDEO_NAME]
                else:
                    video_file_name = f"{event[VIDEO_NAME]}.mp4"
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
        return parsed_events

    def event_section_available_and_is_section_entering(
        self, sections, event_type_available, event
    ):
        return (not event_type_available or event[EVENT_TYPE] == SECTION_ENTER) and (
            event[SECTION_ID] in list(sections.keys())
        )

    def is_event_type_is_available(self, events):
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
