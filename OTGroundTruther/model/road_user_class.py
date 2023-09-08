from dataclasses import dataclass, field
from pathlib import Path

import yaml
from PIL import Image


@dataclass
class RoadUserClass:
    name: str
    label: str
    short_label: str
    key: str | None
    icon_file: Path
    icon: Image = field(init=False)

    def __post_init__(self):
        self.icon = Image.open(self.icon_file)

    def get_name(self) -> str:
        return self.name


@dataclass
class ValidRoadUserClasses:
    _road_user_classes: dict[str, RoadUserClass]

    def get_by_key(self, key: str) -> RoadUserClass | None:
        return self._road_user_classes.get(key)

    def to_dict_with_name_as_key(self) -> dict[str, RoadUserClass]:
        return {value.get_name(): value for value in self._road_user_classes.values()}

    @staticmethod
    def _parse(yaml_content: list[dict[str, dict[str, str]]]):
        road_user_classes = {}
        for road_user_class in yaml_content:
            for name, properties in road_user_class.items():
                key = properties["key"]
                road_user_classes[key] = RoadUserClass(
                    name=name,
                    label=properties["label"],
                    short_label=properties["short_label"],
                    key=key,
                    icon_file=Path(properties["icon_file"]),
                )
        return ValidRoadUserClasses(road_user_classes)

    @staticmethod
    def from_yaml(yaml_file: Path) -> "ValidRoadUserClasses":
        with open(yaml_file, "r") as file:
            try:
                yaml_content = yaml.safe_load(file)
            except yaml.YAMLError:
                print("Unable to parse road_user_classes.yaml, please check")
                raise
        return ValidRoadUserClasses._parse(yaml_content)
