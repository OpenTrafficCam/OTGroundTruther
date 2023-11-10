from dataclasses import dataclass, field
from pathlib import Path

import yaml
from PIL import Image

KEY_YAML_KEY = "key"
SHORT_LABEL_ENG_YAML_KEY = "short_label_eng"
LABEL_YAML_KEY = "label"
ICON_FILE_YAML_KEY = "icon_file"
CLASS_IMAGE_SIZE: int = 80


@dataclass
class RoadUserClass:
    name: str
    label_ger: str
    short_label_eng: str
    key: str | None
    icon_file: Path
    icon: Image = field(init=False)

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


@dataclass
class ValidRoadUserClasses:
    _road_user_classes: dict[str, RoadUserClass]

    def get_by_key(self, key: str) -> RoadUserClass | None:
        return self._road_user_classes.get(key)

    def to_dict_with_name_as_key(self) -> dict[str, RoadUserClass]:
        return {value.get_name(): value for value in self._road_user_classes.values()}

    def get_class_names(self) -> list[str]:
        name_list: list[str] = []
        for road_user_class in list(self._road_user_classes.values()):
            name_list.append(road_user_class.get_name())
        return name_list

    @staticmethod
    def _parse(yaml_content: list[dict[str, dict[str, str]]]):
        road_user_classes = {}
        for road_user_class in yaml_content:
            for name, properties in road_user_class.items():
                key = properties[KEY_YAML_KEY]
                road_user_classes[key] = RoadUserClass(
                    name=name,
                    label_ger=properties[LABEL_YAML_KEY],
                    short_label_eng=properties[SHORT_LABEL_ENG_YAML_KEY],
                    key=key,
                    icon_file=Path(properties[ICON_FILE_YAML_KEY]),
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
