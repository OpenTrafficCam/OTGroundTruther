from dataclasses import dataclass, field
from typing import Iterable, Optional

import cv2
import numpy as np
from PIL import Image

from OTGroundTruther.model.coordinate import Coordinate
from OTGroundTruther.model.event import Event, EventForParsingSerializing
from OTGroundTruther.model.road_user_class import RoadUserClass
from OTGroundTruther.model.video import BackgroundFrame

ACTIVE_COUNT_ID: str = "active-count-id"

COUNT_ID_NAME: str = "ID"
COUNT_CLASS_NAME: str = "Class"
COUNT_ENTER_TIME_NAME: str = "Enter Time"
COUNT_ENTER_GATE_NAME: str = "Enter Gate"
COUNT_EXIT_GATE_NAME: str = "Exit Gate"
COUNT_TIME_SPAN: str = "Time Span"
COUNT_NUMBER_OF_EVENTS: str = "Events"


ARROW_CONTOUR_SIZE: int = 18
COUNT_CONTOUR_COLOR: tuple[int, int, int, int] = (10, 10, 10, 255)
COUNT_CONTOUR_THICKNESS: int = 2
COUNT_LINE_THICKNESS: int = 1

COUNT_TEXT_FONT: int = cv2.FONT_HERSHEY_SIMPLEX
COUNT_TEXT_FONTSCALE: float = 0.5
COUNT_TEXT_COLOR: tuple[int, int, int, int] = (255, 185, 15, 255)
COUNT_TEXT_THICKNESS: int = 1
COUNT_LINETYPE: int = cv2.LINE_AA

NOT_SELECTED_COLOR: tuple[int, int, int, int] = (110, 110, 110, 255)

ACTIVE_COUNT_EVENTPOINT_RADIUS: int = 5
ACTIVE_COUNT_COLOR: tuple[int, int, int, int] = (255, 255, 255, 255)
ACTIVE_COUNT_EVENTPOINT_COLOR: tuple[int, int, int, int] = ACTIVE_COUNT_COLOR
ACTIVE_COUNT_EVENTPOINT_THICKNESS: int = 1
ACTIVE_COUNT_CONTOUR_THICKNESS: int = 4
PLACEHOLDER_ROAD_USER_CLASS: str = "X"
ACTIVE_COUNT_CONTOUR_COLOR: tuple[int, int, int, int] = (255, 255, 255, 255)

ACTIVE_COUNT_EVENTPOINT_BG_RADIUS: int = ACTIVE_COUNT_EVENTPOINT_RADIUS
ACTIVE_COUNT_EVENTPOINT_BG_COLOR: tuple[int, int, int, int] = (10, 10, 10, 255)
ACTIVE_COUNT_EVENTPOINT_BG_THICKNESS: int = ACTIVE_COUNT_EVENTPOINT_THICKNESS + 1

TIME_WINDOW_SHOW_COUNT: float = 1
TIME_WINDOW_EVENT_MOMENT: float = 0.25


COUNT_EVENTPOINT_RADIUS: int = 5
COUNT_EVENTPOINT_COLOR: tuple[int, int, int, int] = (255, 255, 255, 255)
COUNT_EVENTPOINT_THICKNESS = 1

EVENTPOINT_MOMENT_BG_RADIUS: int = COUNT_EVENTPOINT_RADIUS
EVENTPOINT_MOMENT_BG_COLOR: tuple[int, int, int, int] = (255, 0, 0, 255)
EVENTPOINT_MOMENT_BG_THICKNESS: int = 2

EVENTPOINT_MOMENT_RADIUS: int = COUNT_EVENTPOINT_RADIUS
EVENTPOINT_MOMENT_COLOR: tuple[int, int, int, int] = COUNT_EVENTPOINT_COLOR
EVENTPOINT_MOMENT_THICKNESS: int = EVENTPOINT_MOMENT_BG_THICKNESS - 1

IN_FRAME: str = "in_frame"
IN_WINDOW_NOT_IN_FRAME: str = "in_window_not_in_frame"


class TooFewEventsError(Exception):
    pass


class MissingRoadUserClassError(Exception):
    pass


class EventBeforePreviouseEventError(Exception):
    pass


@dataclass
class Count:
    def __init__(
        self,
        road_user_id: str,
        events: list[Event],
        road_user_class: RoadUserClass,
    ):
        self.road_user_id = road_user_id
        self.events = events
        self.road_user_class = road_user_class
        self.get_time_span()

    def __post_init__(self) -> None:
        self._validate()

    def _validate(self):
        if len(self.events) < 2:
            raise TooFewEventsError
        if self.road_user_class is None:
            raise MissingRoadUserClassError

    def get_time_span(self) -> None:
        if len(self.events) > 1:
            self.time_span: float = (
                self.get_last_event().get_timestamp()
                - self.get_first_event().get_timestamp()
            )
        else:
            self.time_span = 0

    def add_event(self, event: Event) -> None:
        self.events.append(event)

    def get_events(self) -> list[Event]:
        return self.events

    def get_road_user_id(self) -> str:
        return self.road_user_id

    def get_road_user_class(self) -> RoadUserClass:
        return self.road_user_class

    def get_first_event(self) -> Event:
        return self.events[0]

    def get_last_event(self) -> Event:
        return self.events[-1]

    def get_properties_to_show_as_dict(self) -> dict[str, str | float]:
        return {
            COUNT_ID_NAME: str(self.get_road_user_id()),
            COUNT_CLASS_NAME: self.get_road_user_class().get_name(),
            COUNT_ENTER_TIME_NAME: self.get_first_event().get_time_as_str(),
            COUNT_ENTER_GATE_NAME: self.get_first_event().get_section().get_name(),
            COUNT_EXIT_GATE_NAME: self.get_last_event().get_section().get_name(),
            COUNT_TIME_SPAN: round(self.time_span, 1),
            COUNT_NUMBER_OF_EVENTS: len(self.get_events()),
        }


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
        return event.get_timestamp() < self._events[-1].get_timestamp()

    def get_events(self) -> list[Event]:
        return self._events

    def set_road_user_class(self, road_user_class: RoadUserClass) -> None:
        self._road_user_class = road_user_class

    def get_road_user_class(self) -> RoadUserClass | None:
        return self._road_user_class


class CountRepository:
    def __init__(self) -> None:
        self._counts: dict[str, Count] = {}
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

    def get_all_as_dict(self) -> dict[str, Count]:
        return self._counts

    def get(self, id: str) -> Optional[Count]:
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

    def delete(self, id: str) -> None:
        """Remove count from the repository.

        Args:
            id (int): the count id to be removed
        """
        print(
            (
                f"deleted count {str(self._counts[id].get_road_user_id())}"
                f" ({self._counts[id].get_road_user_class().get_name()})"
            )
        )
        del self._counts[id]

    def set_current_id(self, id: str | int):
        """set current id

        Args:
            id (str): _description_
        """
        try:
            int_value = int(id)
        except ValueError:
            self._current_id = 0
        else:
            self._current_id = int_value

    def get_id(self) -> str:
        """
        Get an id for a new count
        """
        self._current_id += 1
        candidate = str(self._current_id)
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

    def event_list_to_count_dict(
        self,
        event_list: list[EventForParsingSerializing],
        suffix: str,
    ) -> tuple[bool, dict[str, Count]]:
        """
        create count list from event list and the suitable list of the object ids
        set current id = 0 (only important for id naming of new events later) if the
        ids are not transformable to an int

        Args:
            event_list (list[Event_For_Saving]): List of events.
        """
        events, classes = self._get_events_and_classes_by_id(event_list)
        counts = {}
        for id_ in events.keys():
            if len(events[id_]) >= 2:
                counts[id_ + suffix] = Count(
                    road_user_id=id_ + suffix,
                    events=events[id_],
                    road_user_class=classes[id_],
                )
            else:
                continue  # TODO: Store in "SingleEventRepository"
        compatible = not self.ids_already_exist_in_counts(counts=counts)
        return compatible, counts

    def add_new_counts(
        self,
        new_counts: dict[str, Count],
        keep_existing_counts: bool,
    ) -> None:
        if not keep_existing_counts:
            self.clear()
        self._counts = self._counts | new_counts
        if len(self._counts.keys()) > 0:
            self.set_current_id(list(self._counts.keys())[-1])

    def ids_already_exist_in_counts(self, counts: dict[str, Count]):
        return bool(set(counts.keys()) & set(self._counts.keys()))

    def _get_events_and_classes_by_id(
        self, event_list: list[EventForParsingSerializing]
    ) -> tuple[dict[str, list[Event]], dict[str, RoadUserClass]]:
        events: dict[str, list[Event]] = {}
        classes: dict[str, RoadUserClass] = {}
        for event_for_saving_parsing in event_list:
            id_ = event_for_saving_parsing.get_road_user_id()
            classes[id_] = event_for_saving_parsing.get_road_user_class()
            event_for_saving = event_for_saving_parsing.to_event()
            if id_ in events.keys():
                events[id_] = self.add_event_at_correct_position(
                    events, id_, event_for_saving
                )
            else:
                events[id_] = [event_for_saving]

        return events, classes

    def add_event_at_correct_position(
        self, ordered_events: dict[str, list[Event]], id_: str, event_for_saving: Event
    ) -> list[Event]:
        count_event_list = ordered_events[id_]
        for i, event in enumerate(ordered_events[id_]):
            if event_for_saving.get_timestamp() < event.get_timestamp():
                count_event_list.insert(i, event_for_saving)
                return count_event_list
        count_event_list.append(event_for_saving)
        return count_event_list


@dataclass
class CountsOverlay:
    count_repository: CountRepository
    active_count: ActiveCount | None
    selected_count_ids: list[str]
    background_frame: BackgroundFrame
    selected_classes: list[str]
    image_array: np.ndarray = field(init=False)
    image: Image.Image = field(init=False)

    def __post_init__(self) -> None:
        self._get_image()

    def get(self) -> Image.Image:
        return self.image

    def _get_image(self) -> Image.Image:
        self.image_array = np.zeros(
            (self.background_frame.get_height(), self.background_frame.get_width(), 4),
            dtype=np.uint8,
        )
        self._draw_finished_counts()
        self._draw_selected_counts()
        self._draw_active_count()
        self.image = Image.fromarray(self.image_array)

    def _draw_finished_counts(self) -> None:
        for count in self.count_repository.get_all_as_list():
            if count.get_road_user_id() in self.selected_count_ids:
                continue
            events_to_draw = self._get_events_of_count_to_draw(count)
            if not (events_to_draw[IN_FRAME] + events_to_draw[IN_WINDOW_NOT_IN_FRAME]):
                continue
            if self.selected_count_ids:
                color = NOT_SELECTED_COLOR
                color_contour = NOT_SELECTED_COLOR
            else:
                color = count.get_road_user_class().get_color_rgb() + (255,)
                color_contour = COUNT_CONTOUR_COLOR

                self._draw_events(events_to_draw=events_to_draw)

            self._draw_movement_single_count(
                events=count.get_events(),
                road_user_class=count.get_road_user_class(),
                color=color,
                color_contour=color_contour,
                thickness_contour=COUNT_CONTOUR_THICKNESS,
            )

    def _draw_selected_counts(self) -> None:
        count_dict = self.count_repository.get_all_as_dict()
        for count_id in self.selected_count_ids:
            events_to_draw = self._get_events_of_count_to_draw(count_dict[count_id])
            self._draw_events(events_to_draw=events_to_draw)
            self._draw_movement_single_count(
                events=count_dict[count_id].get_events(),
                road_user_class=count_dict[count_id].get_road_user_class(),
                color=count_dict[count_id].get_road_user_class().get_color_rgb()
                + (255,),
                color_contour=COUNT_CONTOUR_COLOR,
                thickness_contour=COUNT_CONTOUR_THICKNESS,
            )

    def _get_events_of_count_to_draw(self, count: Count) -> dict[str, list[Event]]:
        events_to_draw: dict[str, list[Event]] = {
            IN_FRAME: [],
            IN_WINDOW_NOT_IN_FRAME: [],
        }
        if count.get_road_user_class().get_name() not in self.selected_classes:
            return events_to_draw
        for event in count.get_events():
            if self._is_at_current_frame(event=event):
                events_to_draw[IN_FRAME].append(event)
            elif self._is_in_time_window(
                event=event, time_window=TIME_WINDOW_SHOW_COUNT
            ):
                events_to_draw[IN_WINDOW_NOT_IN_FRAME].append(event)
        return events_to_draw

    def _draw_events(self, events_to_draw: dict[str, list[Event]]) -> None:
        for event in events_to_draw[IN_WINDOW_NOT_IN_FRAME]:
            self._draw_simple_event_circle(event)
        for event in events_to_draw[IN_FRAME]:
            self._draw_event_circle_with_contour(event)

    def _draw_simple_event_circle(self, event: Event) -> None:
        cv2.circle(
            img=self.image_array,
            center=event.get_coordinate().as_list(),
            radius=COUNT_EVENTPOINT_RADIUS,
            color=COUNT_EVENTPOINT_COLOR,
            thickness=COUNT_EVENTPOINT_THICKNESS,
            lineType=COUNT_LINETYPE,
        )

    def _draw_event_circle_with_contour(self, event) -> None:
        cv2.circle(
            img=self.image_array,
            center=event.get_coordinate().as_list(),
            radius=EVENTPOINT_MOMENT_BG_RADIUS,
            color=EVENTPOINT_MOMENT_BG_COLOR,
            thickness=EVENTPOINT_MOMENT_BG_THICKNESS,
            lineType=COUNT_LINETYPE,
        )
        cv2.circle(
            img=self.image_array,
            center=event.get_coordinate().as_list(),
            radius=EVENTPOINT_MOMENT_RADIUS,
            color=EVENTPOINT_MOMENT_COLOR,
            thickness=EVENTPOINT_MOMENT_THICKNESS,
            lineType=COUNT_LINETYPE,
        )

    def _is_at_current_frame(self, event: Event) -> bool:
        return (
            self.background_frame.get_frame_number() == event.get_frame_number()
        ) & (self.background_frame.get_video_file().name == event.get_video_file_name())

    def _is_in_time_window(self, event: Event, time_window: float) -> bool:
        return (
            self.background_frame.get_unix_timestamp() - time_window / 2
            <= event.get_timestamp()
            <= self.background_frame.get_unix_timestamp() + time_window / 2
        )

    def _draw_movement_single_count(
        self,
        events: list[Event],
        road_user_class: RoadUserClass | None,
        color: tuple[int, int, int, int],
        color_contour: tuple[int, int, int, int],
        thickness_contour: int,
    ) -> None:
        for event, next_event in zip(events[:-1], events[1:]):
            p0 = event.get_coordinate()
            p1 = next_event.get_coordinate()
            self._draw_arrow_with_contour(
                p0=p0,
                p1=p1,
                color=color,
                color_contour=color_contour,
                thickness_contour=thickness_contour,
            )
            self._draw_class_text_next_to_arrow(
                p0=p0, p1=p1, road_user_class=road_user_class, color=color
            )

    def _draw_class_text_next_to_arrow(
        self,
        p0: Coordinate,
        p1: Coordinate,
        road_user_class: RoadUserClass | None,
        color: tuple[int, int, int, int],
    ) -> None:
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

    def _draw_arrow_with_contour(
        self,
        p0: Coordinate,
        p1: Coordinate,
        color: tuple[int, int, int, int],
        color_contour: tuple[int, int, int, int],
        thickness_contour: int,
    ) -> None:
        tiplength = self._tiplength_for_same_arrow_size(p0, p1, ARROW_CONTOUR_SIZE)
        cv2.arrowedLine(
            img=self.image_array,
            pt1=p0.as_list(),
            pt2=p1.as_list(),
            color=color_contour,
            thickness=thickness_contour,
            line_type=COUNT_LINETYPE,
            tipLength=tiplength,
        )
        tiplength = self._tiplength_for_same_arrow_size(
            p0,
            p1,
            ARROW_CONTOUR_SIZE - (thickness_contour - COUNT_LINE_THICKNESS),
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

    def _draw_active_count(self) -> None:
        if self.active_count is None:
            return
        if len(self.active_count.get_events()) >= 2:
            self._draw_active_count_multiple_events()
        else:
            for event in self.active_count.get_events():
                self.draw_active_count_only_one_event(event)

    def draw_active_count_only_one_event(self, event: Event) -> None:
        cv2.circle(
            img=self.image_array,
            center=event.get_coordinate().as_list(),
            radius=ACTIVE_COUNT_EVENTPOINT_BG_RADIUS,
            color=ACTIVE_COUNT_EVENTPOINT_BG_COLOR,
            thickness=ACTIVE_COUNT_EVENTPOINT_BG_THICKNESS,
            lineType=COUNT_LINETYPE,
        )
        cv2.circle(
            img=self.image_array,
            center=event.get_coordinate().as_list(),
            radius=ACTIVE_COUNT_EVENTPOINT_RADIUS,
            color=ACTIVE_COUNT_EVENTPOINT_COLOR,
            thickness=ACTIVE_COUNT_EVENTPOINT_THICKNESS,
            lineType=COUNT_LINETYPE,
        )

    def _draw_active_count_multiple_events(self) -> None:
        if self.active_count is not None:
            road_user_class = self.active_count.get_road_user_class()
            if road_user_class is None:
                color = ACTIVE_COUNT_COLOR
            else:
                color = road_user_class.get_color_rgb() + (255,)

            self._draw_movement_single_count(
                events=self.active_count.get_events(),
                road_user_class=road_user_class,
                color=color,
                color_contour=ACTIVE_COUNT_CONTOUR_COLOR,
                thickness_contour=ACTIVE_COUNT_CONTOUR_THICKNESS,
            )

    def _tiplength_for_same_arrow_size(
        self, p0: Coordinate, p1: Coordinate, size: int = 20
    ) -> float:
        length = (
            (p0.get_x() - p1.get_x()) ** 2 + (p0.get_y() - p1.get_y()) ** 2
        ) ** 0.5
        return 1 if length < size or length == 0 else size / length

    def _get_text_position(self, p0: Coordinate, p1: Coordinate) -> tuple[int, int]:
        return (
            int((p0.get_x() + p1.get_x()) / 2),
            int((p0.get_y() + p1.get_y()) / 2),
        )
