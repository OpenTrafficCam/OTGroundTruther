from dataclasses import dataclass, field
from typing import Iterable, Optional

import cv2
import numpy as np
from PIL import Image

from OTGroundTruther.model.coordinate import Coordinate
from OTGroundTruther.model.event import Event, EventForParsingSerializing
from OTGroundTruther.model.road_user_class import RoadUserClass

ACTIVE_COUNT_ID: str = "active-count-id"

ARROW_OUTLINE_SIZE: int = 18
COUNT_OUTLINE_COLOR: tuple[int, int, int, int] = (10, 10, 10, 255)
COUNT_OUTLINE_THICKNESS: int = 2
COUNT_LINE_THICKNESS: int = 1
COUNT_LINE_AND_TEXT_COLOR: tuple[int, int, int, int] = (255, 185, 15, 255)


COUNT_TEXT_FONT: int = cv2.FONT_HERSHEY_SIMPLEX
COUNT_TEXT_FONTSCALE: float = 0.5
COUNT_TEXT_COLOR: tuple[int, int, int, int] = (255, 185, 15, 255)
COUNT_TEXT_THICKNESS: int = 1
COUNT_LINETYPE: int = cv2.LINE_AA

ACTIVE_COUNT_EVENTPOINT_RADIUS: int = 5
ACTIVE_COUNT_COLOR: tuple[int, int, int, int] = (255, 255, 0, 255)
ACTIVE_COUNT_EVENTPOINT_COLOR: tuple[int, int, int, int] = (255, 255, 255, 255)
ACTIVE_COUNT_EVENTPOINT_THICKNESS: int = 1
PLACEHOLDER_ROAD_USER_CLASS: str = "X"


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

    def get_road_user_class(self) -> RoadUserClass | None:
        return self._road_user_class


class CountRepository:
    def __init__(self) -> None:
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
        self._counts[count.road_user_id] = count

    def get_all_as_list(self) -> list[Count]:
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

    def to_event_list(self) -> list[EventForParsingSerializing]:
        """
        get an event list out of the CountRepo
        """
        event_list = []
        for count in self._counts.values():
            for event in count.get_events():
                event_for_save = event.to_event_for_serializing(
                    road_user_id=count.get_road_user_id(),
                    road_user_class=count.get_road_user_class(),
                )
                event_list.append(event_for_save)
        return event_list

    def from_event_list(self, event_list: list[EventForParsingSerializing]) -> None:
        """
        create count list from event list and the suitable list of the object ids

        Args:
            event_list (list[Event_For_Saving]): List of events.
        """
        events, classes = self._get_events_and_classes_by_id(event_list)

        self.clear()
        for id_ in events.keys():
            if len(events[id_]) >= 2:
                self._counts[id_] = Count(
                    road_user_id=id_,
                    events=events[id_],
                    road_user_class=classes[id_],
                )
            else:
                continue  # TODO: Store in "SingleEventRepository"
        if len(self._counts.keys()) > 0:
            self.set_current_id(list(self._counts.keys())[0])

    def _get_events_and_classes_by_id(
        self, event_list: list[EventForParsingSerializing]
    ) -> tuple[dict[int, list[Event]], dict[int, RoadUserClass]]:
        events: dict[int, list[Event]] = {}
        classes: dict[int, RoadUserClass] = {}
        for event_for_saving in event_list:
            id_ = event_for_saving.get_road_user_id()
            if id_ in events.keys():
                events[id_].append(event_for_saving.to_event())
            else:
                classes[id_] = event_for_saving.get_road_user_class()
                events[id_] = [event_for_saving.to_event()]

        return events, classes


@dataclass
class CountsOverlay:
    count_repository: CountRepository
    active_count: ActiveCount | None
    width: int
    height: int
    image_array: np.ndarray = field(init=False)
    image: Image.Image = field(init=False)

    def __post_init__(self) -> None:
        self._get_image()

    def get(self) -> Image.Image:
        return self.image

    def _get_image(self) -> Image.Image:
        self.image_array = np.zeros((self.height, self.width, 4), dtype=np.uint8)
        self._draw_finished_counts()
        if self.active_count is not None:
            self._draw_active_count()
        self.image = Image.fromarray(self.image_array)

    def _draw_finished_counts(self):
        for count in self.count_repository.get_all_as_list():
            self._draw_single_count(
                events=count.get_events(),
                road_user_class=count.get_road_user_class(),
                color=COUNT_LINE_AND_TEXT_COLOR,
            )

    def _draw_single_count(
        self,
        events: list[Event],
        road_user_class: RoadUserClass,
        color: tuple[int, int, int, int],
    ):
        for event, next_event in zip(events[:-1], events[1:]):
            self._draw_arrow_with_text(
                p0=event.get_coordinate(),
                p1=next_event.get_coordinate(),
                road_user_class=road_user_class,
                color=color,
            )

    def _draw_arrow_with_text(
        self,
        p0: Coordinate,
        p1: Coordinate,
        road_user_class: RoadUserClass | None,
        color: tuple[int, int, int, int],
    ) -> None:
        tiplength = self._tiplength_for_same_arrow_size(p0, p1, ARROW_OUTLINE_SIZE)
        cv2.arrowedLine(
            img=self.image_array,
            pt1=p0.as_list(),
            pt2=p1.as_list(),
            color=COUNT_OUTLINE_COLOR,
            thickness=COUNT_OUTLINE_THICKNESS,
            line_type=COUNT_LINETYPE,
            tipLength=tiplength,
        )
        tiplength = self._tiplength_for_same_arrow_size(
            p0,
            p1,
            ARROW_OUTLINE_SIZE - (COUNT_OUTLINE_THICKNESS - COUNT_LINE_THICKNESS),
        )
        cv2.arrowedLine(
            img=self.image_array,
            pt1=p0.as_list(),
            pt2=p1.as_list(),
            color=color,
            thickness=COUNT_LINE_THICKNESS,
            line_type=COUNT_LINETYPE,
            tipLength=tiplength,
        )
        if road_user_class is None:
            text = PLACEHOLDER_ROAD_USER_CLASS
        else:
            text = road_user_class.get_short_label()
        cv2.putText(
            img=self.image_array,
            text=text,
            org=self._get_text_position(p0, p1),
            fontFace=COUNT_TEXT_FONT,
            fontScale=COUNT_TEXT_FONTSCALE,
            color=color,
            thickness=COUNT_TEXT_THICKNESS,
            lineType=COUNT_LINETYPE,
            bottomLeftOrigin=False,
        )

    def _draw_active_count(self):
        if len(self.active_count.get_events()) >= 2:
            self._draw_single_count(
                events=self.active_count.get_events(),
                road_user_class=self.active_count.get_road_user_class(),
                color=ACTIVE_COUNT_COLOR,
            )
        for event in self.active_count.get_events():
            cv2.circle(
                img=self.image_array,
                center=event.get_coordinate().as_list(),
                radius=ACTIVE_COUNT_EVENTPOINT_RADIUS,
                color=ACTIVE_COUNT_EVENTPOINT_COLOR,
                thickness=ACTIVE_COUNT_EVENTPOINT_THICKNESS,
            )

    def _tiplength_for_same_arrow_size(
        self, p0: Coordinate, p1: Coordinate, size: int = 20
    ):
        length = (
            (p0.get_x() - p1.get_x()) ** 2 + (p0.get_y() - p1.get_y()) ** 2
        ) ** 0.5
        return size / length

    def _get_text_position(self, p0: Coordinate, p1: Coordinate):
        return (
            int((p0.get_x() + p1.get_x()) / 2),
            int((p0.get_y() + p1.get_y()) / 2),
        )
