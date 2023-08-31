from OTGroundTruther.cli import CliArgumentParser, CliArguments
from OTGroundTruther.model.count import CountRepository
from OTGroundTruther.model.model import Model
from OTGroundTruther.model.road_user_class import ValidRoadUserClasses
from OTGroundTruther.model.section import SectionParser, SectionRepository
from OTGroundTruther.model.video import Video, VideoRepository

ROAD_USER_CLASSES_YAML_FILE = r"OTGroundTruther/road_user_classes.yaml"


class ModelInitializer:
    def __init__(self):
        parser = CliArgumentParser()
        self._cli_args: CliArguments = parser.parse()
        video_repository = self._get_video_repository()
        section_repository = self._get_sections_repository()
        count_repository = self._get_count_repository()
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

    def _get_count_repository(self):
        # TODO: Get events_file from self._cli_args
        # TODO: Parse Counts from events_file and add_all to count_repository
        return CountRepository()

    def _get_sections_repository(self):
        sections, otanalytics_file_content = SectionParser().parse(
            self._cli_args.sections_file
        )
        section_repository = SectionRepository()
        section_repository.add_all(sections)
        section_repository.set_otanalytics_file_content(otanalytics_file_content)
        return section_repository

    def _get_video_repository(self):
        video_files = [Video(file) for file in self._cli_args.video_files]
        video_repository = VideoRepository()
        video_repository.add_all(video_files)
        return video_repository

    def get(self) -> Model:
        return self._model
