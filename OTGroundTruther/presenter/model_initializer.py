from OTGroundTruther.model.count import CountRepository
from OTGroundTruther.model.model import Model
from OTGroundTruther.model.road_user_class import ValidRoadUserClasses
from OTGroundTruther.model.section import SectionRepository
from OTGroundTruther.model.video import VideoRepository

ROAD_USER_CLASSES_YAML_FILE = r"OTGroundTruther/road_user_classes.yaml"


class ModelInitializer:
    def __init__(self):
        video_repository = VideoRepository()
        section_repository = SectionRepository()
        count_repository = CountRepository()
        active_count = None
        valid_road_user_classes: ValidRoadUserClasses = ValidRoadUserClasses.from_yaml(
            ROAD_USER_CLASSES_YAML_FILE
        )

        self._model = Model(
            video_repository=video_repository,
            section_repository=section_repository,
            count_repository=count_repository,
            active_count=active_count,
            valid_road_user_classes=valid_road_user_classes,
        )

    def get(self) -> Model:
        return self._model
