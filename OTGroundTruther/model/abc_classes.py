from abc import ABC, abstractmethod


class EventForSaving(ABC):
    @abstractmethod
    def to_dict(self) -> dict:
        raise NotImplementedError