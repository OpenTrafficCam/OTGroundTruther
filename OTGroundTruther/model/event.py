from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

from OTGroundTruther.model.coordinate import Coordinate
from OTGroundTruther.model.section import LineSection

from .parse import _parse_bz2, _write_bz2
from .road_user_class import RoadUserClass

METADATA: str = "metadata"
VERSION: str = "version"
SECTION_FORMAT_VERSION: str = "section_file_version"
EVENT_FORMAT_VERSION: str = "event_file_version"
EVENT_LIST = "event_list"
SECTIONS: str = "sections"


@dataclass
class Event_Parent_Class:
    coordinate: Coordinate 
    section: LineSection
    frame_number: int
    timestamp: float
    video_file: Path
    time_created: float


@dataclass
class Event(Event_Parent_Class):
    def to_event_for_saving(self, road_user_id: int, road_user_class: RoadUserClass):
        event_dict = vars(self)
        event_dict["road_user_id"] = road_user_id
        event_dict["road_user_class"] = road_user_class.name
        return Event_For_Saving(**event_dict)

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
class Event_For_Saving(Event_Parent_Class):
    road_user_id: int
    road_user_class: RoadUserClass

    def to_dict(self) -> dict:
        return {
            "event_coordinate": self.coordinate.as_list(),
            "section_id": self.section.name,
            "frame_number": self.frame_number,
            "occurrence": self.timestamp,
            "video_name": self.video_file.stem,
            "time_created": self.time_created,
            "road_user_id": self.road_user_id,
            "road_user_type": self.road_user_class
        }


class EventParser:
    def parse(self, file: Path):
        raise NotImplementedError


class EventListParser():
    def parse(self, otevent_file: Path) -> list[Event]:
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
        for i in range(len(dets_list)):
            section = LineSection(id=dets_list[i]["section_id"], name="to_do",
                                  coordinates=None)
            coordinate = Coordinate(round(dets_list[i]["event_coordinate"][0]),
                                    round(dets_list[i]["event_coordinate"][1]))
            event_list.append(Event(coordinate=coordinate,
                                    section=section,
                                    frame_number=dets_list[i]["frame_number"],
                                    timestamp=dets_list[i]["occurrence"],
                                    video_file=Path(dets_list[i]["video_name"]),
                                    time_created=None,
                                    road_user_id=dets_list[i]["road_user_id"],
                                    road_user_class=dets_list[i]["road_user_type"]))
        return event_list

    def serialize(
        self, events: Iterable[Event_For_Saving],
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
        self, events: Iterable[Event_For_Saving], sections: Iterable[LineSection]
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

    def _convert_events(self, events: Iterable[Event_For_Saving]) -> list[dict]:
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
    