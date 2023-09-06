from pathlib import Path

from OTGroundTruther.cli import CliArgumentParser, CliArguments
from OTGroundTruther.model.count import CountRepository
from OTGroundTruther.model.event import EventListParser
from OTGroundTruther.model.model import Model
from OTGroundTruther.model.road_user_class import ValidRoadUserClasses
from OTGroundTruther.model.section import SectionParser, SectionRepository
from OTGroundTruther.model.video import Video, VideoRepository

ROAD_USER_CLASSES_YAML_FILE: Path = Path(r"OTGroundTruther/road_user_classes_v1_2.yaml")


class ModelInitializer:
    def __init__(self) -> None:
        parser = CliArgumentParser()
        cli_args: CliArguments = parser.parse()
        self._valid_road_user_classes: ValidRoadUserClasses = (
            ValidRoadUserClasses.from_yaml(ROAD_USER_CLASSES_YAML_FILE)
        )
        self._create_repositories()
        self._prefill_repositories(cli_args)
        active_count = None
        self._model = Model(
            video_repository=self._video_repository,
            section_repository=self._section_repository,
            count_repository=self._count_repository,
            active_count=active_count,
            valid_road_user_classes=self._valid_road_user_classes,
        )

    def _create_repositories(self) -> None:
        self._video_repository = VideoRepository()
        self._section_repository = SectionRepository()
        self._count_repository = CountRepository()

    def _prefill_repositories(self, cli_args: CliArguments) -> None:
        if cli_args.video_files:
            self._prefill_video_repository(files=cli_args.video_files)
        if cli_args.events_file is not None:
            self._prefill_section_repository(file=cli_args.events_file)
            self._prefill_count_repository(file=cli_args.events_file)
        elif cli_args.sections_file is not None:
            self._prefill_section_repository(file=cli_args.sections_file)

    def _prefill_video_repository(self, files: set[Path]) -> None:
        video_files = [Video(file) for file in files]
        self._video_repository.add_all(video_files)

    def _prefill_section_repository(self, file: Path) -> None:
        sections, otanalytics_file_content = SectionParser().parse(file)
        self._section_repository.add_all(sections)
        self._section_repository.set_otanalytics_file_content(otanalytics_file_content)

    def _prefill_count_repository(self, file: Path) -> None:
        event_list = EventListParser().parse(
            otevent_file=file,
            sections=self._section_repository.get_all_as_dict(),
            valid_road_user_classes=self._valid_road_user_classes,
        )
        self._count_repository.from_event_list(event_list)

    def get(self) -> Model:
        return self._model
