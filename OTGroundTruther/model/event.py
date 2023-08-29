from dataclasses import dataclass
from pathlib import Path

from OTGroundTruther.model.coordinate import Coordinate
from OTGroundTruther.model.section import LineSection


@dataclass
class Event:
    coordinate: Coordinate
    section: LineSection
    frame: int
    timestamp: float
    video: str
    time_created: float

    def to_dict(self) -> dict:
        return {
            "coordinate": self.coordinate,
            "section": self.section,
            "frame": self.frame,
            "timestamp": self.timestamp,
            "video": self.video,
            "time_created": self.time_created,
        }


class EventParser:
    def parse(self, file: Path):
        raise NotImplementedError
