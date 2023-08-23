from dataclasses import dataclass
from math import atan2, dist

import numpy as np

from .coordinate import Coordinate


@dataclass
class Ellipse:
    start: Coordinate
    end: Coordinate
    relative_height: int

    def contains(self, coordinate: Coordinate) -> bool:
        section_middle_point_x = (self.start.x + self.end.x) / 2
        section_middle_point_y = (self.start.y + self.end.y) / 2
        delta_x = coordinate.x - section_middle_point_x
        # mirror the y-values because the y-axis in the frame is mirrored
        delta_y = -coordinate.y + section_middle_point_y
        radian = atan2(self.end.y - self.start.y, self.start.x - self.end.x)
        a = dist(self.start.as_tuple(), self.end.as_tuple()) / 2
        b = a * self.relative_height
        # turned ellipse equation
        return (delta_x * np.cos(radian) + delta_y * np.sin(radian)) ** 2 / a**2 + (
            delta_x * np.sin(radian) - delta_y * np.cos(radian)
        ) ** 2 / b**2 <= 1
