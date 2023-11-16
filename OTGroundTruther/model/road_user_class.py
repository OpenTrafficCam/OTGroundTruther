from dataclasses import dataclass, field
from pathlib import Path

import yaml
from PIL import Image

KEY_YAML_KEY = "key"
SHORT_LABEL_ENG_YAML_KEY = "short_label_eng"
LABEL_YAML_KEY = "label"
ICON_FILE_YAML_KEY = "icon_file"
COLOR_NAME_YAML_KEY = "color_name"
COLOR_RGB_YAML_KEY = "color_rgb"

CLASS_IMAGE_SIZE: int = 80


class YamlWrongStructureError(Exception):
    pass


@dataclass
class RoadUserClass:
    name: str
    label_ger: str
    short_label_eng: str
    key: str | None
    icon_file: Path
    icon: Image = field(init=False)
    color_name: str
    color_rgb: tuple[int, int, int]

    def __post_init__(self):
        self.icon = Image.open(self.icon_file).resize(
            (CLASS_IMAGE_SIZE, CLASS_IMAGE_SIZE)
        )

    def get_name(self) -> str:
        return self.name

    def get_short_label(self) -> str:
        return self.short_label_eng

    def get_icon(self) -> Image:
        return self.icon

    def get_key(self) -> str | None:
        return self.key

    def get_color_rgb(self) -> tuple[int, int, int]:
        return self.color_rgb


@dataclass
class ValidRoadUserClasses:
    def __init__(
        self, yaml_content: list[dict[str, dict[str, str | dict[str, int]]]]
    ) -> None:
        self._road_user_classes: dict[str, RoadUserClass] = self._parse(
            yaml_content=yaml_content
        )

    def get_by_key(self, key: str) -> RoadUserClass | None:
        return self._road_user_classes.get(key)

    def to_dict_with_name_as_key(self) -> dict[str, RoadUserClass]:
        return {value.get_name(): value for value in self._road_user_classes.values()}

    def to_dict_key_with_name(self) -> dict[str, str]:
        return {
            str(class_.get_key()): class_.get_name()
            for class_ in self._road_user_classes.values()
        }

    def get_class_names(self) -> list[str]:
        name_list: list[str] = []
        for road_user_class in list(self._road_user_classes.values()):
            name_list.append(road_user_class.get_name())
        return name_list

    def _parse(
        self, yaml_content: list[dict[str, dict[str, str | dict[str, int]]]]
    ) -> dict[str, RoadUserClass]:
        road_user_classes = {}
        for road_user_class in yaml_content:
            for name, properties in road_user_class.items():
                key = str(properties[KEY_YAML_KEY])
                road_user_classes[key] = self._prove_and_get_road_user_class(
                    properties, name
                )
        return road_user_classes

    def _prove_and_get_road_user_class(
        self,
        properties: dict[str, str | dict[str, int]],
        name: str,
    ) -> RoadUserClass:
        color_rgb_dict = properties[COLOR_RGB_YAML_KEY]
        if type(color_rgb_dict) is dict:
            r = int(list(color_rgb_dict.values())[0])
            g = int(list(color_rgb_dict.values())[1])
            b = int(list(color_rgb_dict.values())[2])
            return RoadUserClass(
                name=name,
                label_ger=str(properties[LABEL_YAML_KEY]),
                short_label_eng=str(properties[SHORT_LABEL_ENG_YAML_KEY]),
                key=str(properties[KEY_YAML_KEY]),
                icon_file=Path(str(properties[ICON_FILE_YAML_KEY])),
                color_name=str(properties[COLOR_NAME_YAML_KEY]),
                color_rgb=(r, g, b),
            )
        raise YamlWrongStructureError

    @staticmethod
    def from_yaml(yaml_file: Path) -> "ValidRoadUserClasses":
        with open(yaml_file, "r") as file:
            try:
                yaml_content = yaml.safe_load(file)
            except yaml.YAMLError:
                print("Unable to parse road_user_classes.yaml, please check")
                raise
        return ValidRoadUserClasses(yaml_content)
