from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Optional, Sequence

from .coordinate import Coordinate
from .ellipse import Ellipse
from .parse import parse

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


class UnambigousSectionEllipsesError(Exception):
    pass


@dataclass(frozen=True)
class LineSection:
    id: str
    name: str
    coordinates: list[Coordinate]

    def ellipses_contain(self, coordinate: Coordinate, relative_ellipse_height: float):
        for i in range(len(self.coordinates) - 1):
            start = coordinate[i]
            end = coordinate[i + 1]
            if Ellipse(start, end, relative_height=relative_ellipse_height).contains(
                coordinate
            ):
                return True


@dataclass
class SectionRepository:
    _sections: dict[str, LineSection] = {}
    _otanalytics_file_content: dict = {}

    def add_all(self, sections: Iterable[LineSection]) -> None:
        """Add several sections at once to the repository.

        Args:
            sections (Iterable[Section]): the sections to add
        """
        for section in sections:
            self._add(section)
            # TODO: Check if Ellipses around different sections touch each other

    def _add(self, section: LineSection) -> None:
        """Internal method to add sections without notifying observers.

        Args:
            section (Section): the section to be added
        """
        self._sections[section.id] = section

    def get_all(self) -> list[LineSection]:
        """Get all sections from the repository.

        Returns:
            Iterable[Section]: the sections
        """
        return list(self._sections.values())

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
            for section in self.get_all()
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
