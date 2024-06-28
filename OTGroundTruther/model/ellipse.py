from dataclasses import dataclass, field
from math import atan2, dist, pi

import numpy as np

from OTGroundTruther.model.coordinate import Coordinate

RELATIVE_HEIGHT: float = 0.15
MINOR_AXIS_LENGTH_SET: bool = True
MINOR_AXIS_LENGTH: float = 10


@dataclass
class Ellipse:
    start: Coordinate
    end: Coordinate
    relative_height: float = field(init=False)
    center: Coordinate = field(init=False)
    radian: float = field(init=False)
    angle: float = field(init=False)
    major_axis_length: float = field(init=False)
    minor_axis_length: float = field(init=False)

    def __post_init__(self) -> None:
        self._calculate_parameters()

    def _calculate_parameters(self):
        self.center = Coordinate(
            x=round((self.start.x + self.end.x) / 2),
            y=round((self.start.y + self.end.y) / 2),
        )
        self.radian = atan2(self.end.y - self.start.y, self.start.x - self.end.x)
        self.angle = -self.radian * (180 / pi)
        self.major_axis_length = dist(self.start.as_tuple(), self.end.as_tuple()) / 2
        if MINOR_AXIS_LENGTH_SET:
            self.minor_axis_length = MINOR_AXIS_LENGTH
            self.relative_height = self.minor_axis_length / self.major_axis_length
        else:
            self.minor_axis_length = self.major_axis_length * RELATIVE_HEIGHT
            self.relative_height = RELATIVE_HEIGHT

    def contains(self, coordinate: Coordinate) -> bool:
        delta_x = coordinate.x - self.center.x
        delta_y = -coordinate.y + self.center.y
        return (
            delta_x * np.cos(self.radian) + delta_y * np.sin(self.radian)
        ) ** 2 / self.major_axis_length**2 + (
            delta_x * np.sin(self.radian) - delta_y * np.cos(self.radian)
        ) ** 2 / self.minor_axis_length**2 <= 1
