from dataclasses import dataclass


@dataclass
class Coordinate:
    x: int
    y: int

    def as_tuple(self):
        return self.x, self.y

    def as_list(self):
        return [self.x, self.y]

    def to_dict(self):
        return {"x": self.x, "y": self.y}

    def get_x(self):
        return self.x

    def get_y(self):
        return self.y
