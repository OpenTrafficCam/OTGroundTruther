from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

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


@dataclass
class Event:
    coordinate: Coordinate
    section: LineSection
    frame_number: int
    timestamp: float
    video_file: Path
    time_created: float

    def to_event_for_serializing(
        self, road_user_id: int, road_user_class: RoadUserClass
    ) -> "EventForParsingSerializing":
        event: dict = vars(self)
        event[ROAD_USER_ID] = road_user_id
        event[ROAD_USER_CLASS] = road_user_class
        return EventForParsingSerializing(**event)

    def to_dict(self) -> dict:
        return {
            EVENT_COORDINATE: self.coordinate.as_list(),
            SECTION_ID: self.section.name,
            FRAME_NUMBER: self.frame_number,
            OCCURENCE: self.timestamp,
            VIDEO_NAME: self.video_file.stem,
            TIME_CREATED: self.time_created,
        }


@dataclass
class EventForParsingSerializing:
    coordinate: Coordinate
    section: LineSection
    frame_number: int
    timestamp: float
    video_file: Path
    time_created: float
    road_user_id: int
    road_user_class: RoadUserClass

    def to_event(self) -> Event:
        event_dict = vars(self)
        event_dict.pop(ROAD_USER_ID)
        event_dict.pop(ROAD_USER_CLASS)
        return Event(**event_dict)

    def to_dict(self) -> dict:
        return {
            EVENT_COORDINATE: self.coordinate.as_list(),
            SECTION_ID: self.section.name,
            FRAME_NUMBER: self.frame_number,
            OCCURENCE: self.timestamp,
            VIDEO_NAME: self.video_file.stem,
            TIME_CREATED: self.time_created,
            ROAD_USER_ID: self.road_user_id,
            ROAD_USER_CLASS_OTEVENTS: self.road_user_class.get_name(),
            DIRECTION_VECTOR: None,
        }

    def get_road_user_id(self) -> int:
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
        """Parse otevents file and convert its content to domain level objects namely
        `Events`s.

        Args:
            otevent_file (Path): the file to

        Returns:
            list[Event]: the events.
        """
        otevents_content = parse(otevent_file)
        events: list[dict] = otevents_content[EVENT_LIST]
        parsed_events = []
        classes_by_name = valid_road_user_classes.to_dict_with_name_as_key()
        for event in events:
            if event[SECTION_ID] in list(sections.keys()):
                section = sections[event[SECTION_ID]]
                coordinate = Coordinate(
                    round(event[EVENT_COORDINATE][0]),
                    round(event[EVENT_COORDINATE][1]),
                )
                road_user_class = classes_by_name[event[ROAD_USER_CLASS_OTEVENTS]]

                parsed_events.append(
                    EventForParsingSerializing(
                        coordinate=coordinate,
                        section=section,
                        frame_number=event[FRAME_NUMBER],
                        timestamp=event[OCCURENCE],
                        video_file=Path(event[VIDEO_NAME]),
                        time_created=0,
                        road_user_id=event[ROAD_USER_ID],
                        road_user_class=road_user_class,
                    )
                )
        return parsed_events

    def serialize(
        self,
        events: Iterable[EventForParsingSerializing],
        sections: dict[str, LineSection],
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
        events: Iterable[EventForParsingSerializing],
        sections: dict[str, LineSection],
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

    def _convert_events(
        self, events: Iterable[EventForParsingSerializing]
    ) -> list[dict]:
        """Convert events to dictionary.

        Args:
            events (Iterable[Event]): events to convert

        Returns:
            list[dict]: list containing raw information of events
        """
        return [event.to_dict() for event in events]

    def _convert_sections(self, sections: dict[str, LineSection]) -> list[dict]:
        """Convert sections to dictionary

        Args:
            sections (Iterable[Section]): sections to convert

        Returns:
            list[dict]: list containing raw information of sections
        """
        return [section.to_dict() for section in sections.values()]
