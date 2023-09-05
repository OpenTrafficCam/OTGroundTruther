from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

from OTGroundTruther.model.coordinate import Coordinate
from OTGroundTruther.model.road_user_class import ValidRoadUserClasses
from OTGroundTruther.model.section import LineSection

from .abc_classes import EventForSaving
from .parse import _parse_bz2, _write_bz2
from .road_user_class import RoadUserClass

METADATA: str = "metadata"
VERSION: str = "version"
SECTION_FORMAT_VERSION: str = "section_file_version"
EVENT_FORMAT_VERSION: str = "event_file_version"
EVENT_LIST = "event_list"
SECTIONS: str = "sections"


@dataclass
class Event:
    coordinate: Coordinate
    section: LineSection
    frame_number: int
    timestamp: float
    video_file: Path
    time_created: float

    def to_event_for_saving(
            self, road_user_id: int, road_user_class: RoadUserClass
            ) -> EventForSaving:
        
        event_dict = vars(self)
        event_dict["road_user_id"] = road_user_id
        event_dict["road_user_class"] = road_user_class
        return EventForSaving(**event_dict)

    def to_dict(self) -> dict:
        return {
            "event_coordinate": self.coordinate.as_list(),
            "section_id": self.section.name,
            "frame_number": self.frame_number,
            "occurrence": self.timestamp,
            "video_name": self.video_file.stem,
            "time_created": self.time_created,
        }


@dataclass
class EventForSaving:
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
        event_dict.pop("road_user_id")
        event_dict.pop("road_user_class")
        return Event(**event_dict)

    def to_dict(self) -> dict:
        return {
            "event_coordinate": self.coordinate.as_list(),
            "section_id": self.section.name,
            "frame_number": self.frame_number,
            "occurrence": self.timestamp,
            "video_name": self.video_file.stem,
            "time_created": self.time_created,
            "road_user_id": self.road_user_id,
            "road_user_type": self.road_user_class.get_name(),
            "direction_vector": None
        }

    def get_road_user_id(self) -> int:
        return self.road_user_id

    def get_road_user_class(self) -> RoadUserClass:
        return self.road_user_class


class EventParser:
    def parse(self, file: Path):
        raise NotImplementedError


class EventListParser():
    def parse(self, otevent_file: Path,
              sections_dict: dict[str, LineSection],
              valid_road_user_classes: ValidRoadUserClasses) -> list[EventForSaving]:
        """Parse otevents file and convert its content to domain level objects namely
        `Events`s.

        Args:
            otevent_file (Path): the file to

        Returns:
            list[Event]: the events.
        """
        otevent_dict = _parse_bz2(otevent_file)
        dets_list: list[dict] = otevent_dict[EVENT_LIST]
        event_list = []
        classes_by_name = valid_road_user_classes.to_dict_with_name_as_key()
        for i in range(len(dets_list)):
            if dets_list[i]["section_id"] in list(sections_dict.keys()):
                section = sections_dict[dets_list[i]["section_id"]]
                coordinate = Coordinate(round(dets_list[i]["event_coordinate"][0]),
                                        round(dets_list[i]["event_coordinate"][1]))
                road_user_class = classes_by_name[dets_list[i]["road_user_type"]]

                event_list.append(EventForSaving(coordinate=coordinate,
                                  section=section,
                                  frame_number=dets_list[i]["frame_number"],
                                  timestamp=dets_list[i]["occurrence"],
                                  video_file=Path(dets_list[i]["video_name"]),
                                  time_created=0,
                                  road_user_id=dets_list[i]["road_user_id"],
                                  road_user_class=road_user_class))
        return event_list

    def serialize(
        self, events: Iterable[EventForSaving],
        sections: Iterable[LineSection], file: Path
    ) -> None:
        """Serialize event list into file.

        Args:
            events (Iterable[Event]): events to serialize
            sections (Section): sections to serialize
            file (Path): file to serialize events and sections to
        """
        content = self._convert(events, sections)
        _write_bz2(content, file)

    def _convert(
        self, events: Iterable[EventForSaving], sections: Iterable[LineSection]
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

    def _convert_events(self, events: Iterable[EventForSaving]) -> list[dict]:
        """Convert events to dictionary.

        Args:
            events (Iterable[Event]): events to convert

        Returns:
            list[dict]: list containing raw information of events
        """
        return [event.to_dict() for event in events]

    def _convert_sections(self, sections: Iterable[LineSection]) -> list[dict]:
        """Convert sections to dictionary

        Args:
            sections (Iterable[Section]): sections to convert

        Returns:
            list[dict]: list containing raw information of sections
        """
        return [section.to_dict() for section in sections.values()]
    