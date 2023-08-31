from dataclasses import dataclass
from pathlib import Path

from OTGroundTruther.model.coordinate import Coordinate
from OTGroundTruther.model.section import LineSection


@dataclass
class Event:
    coordinate: Coordinate
    section: LineSection
    frame_number: int
    timestamp: float
    video_file: Path
    time_created: float

    def to_dict(self) -> dict:
        return {
            "coordinate": self.coordinate.as_tuple(),
            "section": self.section.name,
            "frame": self.frame_number,
            "timestamp": self.timestamp,
            "video": self.video_file.stem,
            "time_created": self.time_created,
        }


class EventParser:
    def parse(self, file: Path):
        raise NotImplementedError
