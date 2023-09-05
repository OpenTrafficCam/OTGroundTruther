from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Optional, Sequence

import cv2
import numpy as np
from PIL import Image

from OTGroundTruther.model.coordinate import Coordinate
from OTGroundTruther.model.ellipse import Ellipse
from OTGroundTruther.model.parse import parse

SECTIONS: str = "sections"
ID: str = "id"
NAME: str = "name"
TYPE_: str = "type"
LINE: str = "line"
AREA: str = "area"
COORDINATES: str = "coordinates"
RELATIVE_OFFSET_COORDINATES: str = "relative_offset_coordinates"
PLUGIN_DATA: str = "plugin_data"
METADATA: str = "metadata"

SECTION_COLOR = (200, 125, 125, 255)
ELLIPSE_COLOR = (127, 255, 0, 255)
SECTION_THICKNESS = 2
ELLIPSE_THICKNESS = 1


class UnambigousSectionEllipsesError(Exception):
    pass


@dataclass
class LineSection:
    id: str
    name: str
    coordinates: list[Coordinate]
    ellipses: list[Ellipse] = field(init=False)

    def __post_init__(self) -> None:
        if self.coordinates is not None:
            self.ellipses = self._get_ellipses()

    def _get_ellipses(self) -> None:
        ellipses = []
        for i in range(len(self.coordinates) - 1):
            start = self.coordinates[i]
            end = self.coordinates[i + 1]
            ellipses.append(Ellipse(start, end))
        return ellipses

    def ellipses_contain(self, coordinate: Coordinate):
        for ellipse in self.ellipses:
            if ellipse.contains(coordinate):
                return True
    
    def to_dict(self) -> dict:
        coordinates = self._get_coordinate_list()
        return {
            "id": self.id,
            "name": self.name,
            "type": "line",
            "relative_offset_coordinates": {
                "section-enter": {
                    "x": 0.5,
                    "y": 0.5
                }
            },
            "coordinates": coordinates,
            "plugin_data": {}
        }

    def _get_coordinate_list(self):
        return [coordinate.to_dict() for coordinate in self.coordinates]


@dataclass
class SectionsOverlay:
    sections: list[LineSection]
    width: int
    height: int
    image: Image.Image = field(init=False)

    def __post_init__(self) -> None:
        self._get_image()

    def get(self) -> Image.Image:
        return self.image

    def _get_image(self) -> Image.Image:
        image_array = np.zeros((self.height, self.width, 4), dtype=np.uint8)
        for section in self.sections:
            for ellipse in section.ellipses:
                self._draw_line(image_array, ellipse)
                self._draw_ellipse(image_array, ellipse)
        self.image = Image.fromarray(image_array)

    def _draw_line(self, image_array: np.array, ellipse: Ellipse) -> None:
        return cv2.line(
            img=image_array,
            pt1=ellipse.start.as_tuple(),
            pt2=ellipse.end.as_tuple(),
            color=SECTION_COLOR,
            thickness=SECTION_THICKNESS,
        )

    def _draw_ellipse(self, image_array: np.array, ellipse: Ellipse) -> None:
        return cv2.ellipse(
            img=image_array,
            center=ellipse.center.as_tuple(),
            axes=(round(ellipse.major_axis_length), round(ellipse.minor_axis_length)),
            angle=ellipse.angle,
            startAngle=0,
            endAngle=360,
            color=ELLIPSE_COLOR,
            thickness=ELLIPSE_THICKNESS,
        )


class SectionRepository:
    def __init__(self):
        self._sections: dict[str, LineSection] = {}
        self._otanalytics_file_content: dict = {}

    def add_all(self, sections: Iterable[LineSection]) -> None:
        """Add several sections at once to the repository.

        Args:
            sections (Iterable[Section]): the sections to add
        """
        for section in sections:
            self._add(section)
            # TODO: Check if ellipses around different sections touch each other

    def _add(self, section: LineSection) -> None:
        """Internal method to add sections without notifying observers.

        Args:
            section (Section): the section to be added
        """
        self._sections[section.id] = section

    def get_all_as_list(self) -> list[LineSection]:
        """Get all sections from the repository as list.

        Returns:
            Iterable[Section]: the sections
        """
        return list(self._sections.values())

    def get_all_as_dict(self) -> dict[str, LineSection]:
        """Get all sections from the repository as dict.

        Returns:
            dict[str, LineSection]: the sections
        """
        return self._sections

    def get(self, id: str) -> Optional[LineSection]:
        """Get the section for the given id or nothing, if the id is missing.

        Args:
            id (SectionId): id to get section for

        Returns:
            Optional[Section]: section if present
        """
        return self._sections.get(id)

    def get_by_coordinate(self, coordinate: Coordinate) -> LineSection | None:
        filtered_sections = [
            section
            for section in self.get_all_as_list()
            if section.ellipses_contain(coordinate)
        ]
        if len(filtered_sections) > 1:
            raise UnambigousSectionEllipsesError
        elif not filtered_sections:
            return None
        else:
            return filtered_sections[0]

    def set_otanalytics_file_content(self, otanalytics_file_content: dict):
        self._otanalytics_file_content = otanalytics_file_content

    def get_otanalytics_file_content(self) -> dict:
        return self._otanalytics_file_content

    def is_empty(self) -> bool:
        return not self._sections

    def clear(self) -> None:
        """
        Clear the repository and inform the observers about the empty repository.
        """
        self._sections.clear()
        self._otanalytics_file_content.clear()


class SectionParser:
    """
    Parse a flow file and convert its content to domain objects namely
    Flow, LineSection, Area and Coordinate.

    Args:
        FlowParser (FlowParser): extends FlowParser interface
    """

    def parse(self, file: Path) -> tuple[Sequence[LineSection], dict]:
        """Parse the content of the file into Flow and Section objects.

        Args:
            file (Path): path to flow file

        Returns:
            list[Section]: list of Section objects
            dict: dict of OTAnalytics metadata
        """
        content: dict = parse(file)
        section_content = content.get(SECTIONS, [])
        sections = [self.parse_section(entry) for entry in section_content]
        return sections, content

    def parse_section(self, entry: dict) -> LineSection:
        """Parse sections by type.

        Args:
            entry (dict): content of section file

        Raises:
            UnknownSectionType: if the type of a section is unknown

        Returns:
            Section: section of parsed type
        """
        type_ = entry.get(TYPE_)
        if type_ == LINE:
            return self._parse_line_section(entry)
        else:
            raise ValueError("Areas are not supported in OTGroundTruther")

    def _parse_line_section(self, data: dict) -> LineSection:
        """Parse data to line section.

        Args:
            data (dict): data to parse to line section

        Returns:
            Section: line section
        """
        section_id = self._parse_section_id(data)
        name = self._parse_name(data)
        coordinates = self._parse_coordinates(data)
        return LineSection(id=section_id, name=name, coordinates=coordinates)

    def _parse_section_id(self, data: dict) -> str:
        return data[ID]

    def _parse_name(self, data: dict) -> str:
        _id = data[ID]
        return data.get(NAME, _id)

    def _parse_coordinates(self, data: dict) -> list[Coordinate]:
        """Parse data to coordinates.

        Args:
            data (dict): data to parse to coordinates

        Returns:
            list[Coordinate]: coordinates
        """
        return [self._parse_coordinate(entry) for entry in data[COORDINATES]]

    def _parse_coordinate(self, data: dict) -> Coordinate:
        """Parse data to coordinate.

        Args:
            data (dict): data to parse to coordinate

        Returns:
            Coordinate: coordinate
        """
        return Coordinate(
            x=data.get("x", 0),
            y=data.get("y", 0),
        )
