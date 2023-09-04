from dataclasses import dataclass
from typing import Iterable, Optional

from OTGroundTruther.model.event import Event, Event_For_Saving
from OTGroundTruther.model.road_user_class import RoadUserClass

ACTIVE_COUNT_ID = "active-count-id"


class TooFewEventsError(Exception):
    pass


class MissingRoadUserClassError(Exception):
    pass


class EventBeforePreviouseEventError(Exception):
    pass


@dataclass
class Count:
    road_user_id: int
    events: list[Event]
    road_user_class: RoadUserClass

    def __post_init__(self) -> None:
        self._validate()

    def _validate(self):
        if len(self.events) < 2:
            raise TooFewEventsError
        if self.road_user_class is None:
            raise MissingRoadUserClassError

    def add_id_and_class_to_events(self) -> None:
        for i in range(len(self.events)):
            self.events[i].road_user_id = self.road_user_id
            self.events[i].road_user_class = self.road_user_class

    def add_event(self, event: Event) -> None:
        self.events.append(event)

    def get_events(self) -> list[Event]:
        return self.events

    def get_road_user_id(self) -> int:
        return self.road_user_id

    def get_road_user_class(self) -> RoadUserClass:
        return self.road_user_class


class ActiveCount:
    def __init__(
        self,
        first_event: Event | None = None,
        road_user_class: RoadUserClass | None = None,
    ):
        self._events: list[Event] = [first_event] if first_event is not None else []
        self._road_user_class: RoadUserClass | None = (
            road_user_class if road_user_class is not None else None
        )

    def add_event(self, event: Event):
        if self._new_event_earlier_than_previous(event):
            raise EventBeforePreviouseEventError
        if self._new_event_has_same_section_as_previous(event):
            self._replace_previous_event_with(event)
        else:
            self._events.append(event)

    def _replace_previous_event_with(self, event: Event):
        self._events[-1] = event

    def _new_event_has_same_section_as_previous(self, event: Event):
        return event.section == self._events[-1].section

    def _new_event_earlier_than_previous(self, event: Event):
        return event.frame_number < self._events[-1].frame_number

    def get_events(self) -> list[Event]:
        return self._events

    def set_road_user_class(self, road_user_class: RoadUserClass) -> None:
        self._road_user_class = road_user_class

    def get_road_user_class(self) -> RoadUserClass:
        return self._road_user_class


@dataclass
class CountsOverlay:
    # TODO
    pass


class CountRepository:
    def __init__(self):
        self._counts: dict[int, Count] = {}
        self._current_id: int = 0

    def add_all(self, counts: Iterable[Count]) -> None:
        """Add several counts at once to the repository.

        Args:
            counts (Iterable[Count]): the counts to add
        """
        for count in counts:
            self.add(count)

    def add(self, count: Count) -> None:
        """Add a single count.

        Args:
            count (Count): the count to be added
        """
        self._counts[count.id] = count

    def get_all(self) -> list[Count]:
        """Get all counts from the repository.

        Returns:
            Iterable[Counts]: the counts
        """
        return list(self._counts.values())

    def get(self, id: int) -> Optional[Count]:
        """Get the count for the given id or nothing, if the id is missing.

        Args:
            id (int): id to get count for

        Returns:
            Optional[Count]: count if present
        """
        return self._counts.get(id)

    def get_by_frame_of_events(self, frame: int) -> list[Count]:
        filtered_counts: list[Count] = []
        for count in self._counts.values():
            filtered_counts.extend(
                count for event in count.events if event.frame_number == frame
            )
        return list(set(filtered_counts))

    def remove(self, id: int) -> None:
        """Remove count from the repository.

        Args:
            id (int): the count id to be removed
        """
        del self._counts[id]
    
    def set_current_id(self, id: int):
        """set current id

        Args:
            id (int): _description_
        """
        self._current_id = id

    def get_id(self) -> int:
        """
        Get an id for a new count
        """
        self._current_id += 1
        candidate = self._current_id
        return self.get_id() if candidate in self._counts.keys() else candidate

    def is_empty(self) -> bool:
        return not self._counts

    def clear(self) -> None:
        """
        Clear the repository.
        """
        self._counts.clear()

    def to_event_list(self) -> list[Event_For_Saving]:
        """"
        get an event list out of the CountRepo
        """
        event_list = []
        for count in self._counts.values():
            for event in count.get_events():
                event_for_save = event.to_event_for_saving(
                    road_user_id=count.get_road_user_id,
                    road_user_class=count.get_road_user_class)
                event_list.append(event_for_save)
        return event_list
    
    def from_event_list(self, event_list: list[Event]) -> None:
        """
        create count list from event list and the suitable list of the object ids

        Args:
            event_list (list[Event]): _description_
        """
        self._counts = {}
        for event in event_list:
            if event.road_user_id in self._counts.keys():
                self._counts[event.road_user_id].add_event(event)
            else:
                self._counts[
                    event.road_user_id
                ] = Count(road_user_id=event.road_user_id,
                          events=[event],
                          road_user_class=event.road_user_class)

        self.set_current_id(list(self._counts.keys())[0])

        



