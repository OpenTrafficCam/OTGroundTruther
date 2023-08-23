from dataclasses import dataclass


@dataclass
class Coordinate:
    x: int
    y: int

    def as_tuple(self):
        return self.x, self.y
