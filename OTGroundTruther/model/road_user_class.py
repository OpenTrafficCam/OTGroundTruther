from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class RoadUserClass:
    name: str

    def __str__(self) -> str:
        pass
