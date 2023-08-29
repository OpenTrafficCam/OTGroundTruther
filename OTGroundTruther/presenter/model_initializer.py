from OTGroundTruther.model.count import CountRepository
from OTGroundTruther.model.model import Model
from OTGroundTruther.model.section import SectionRepository
from OTGroundTruther.model.video import VideoRepository


class ModelInitializer:
    def __init__(self):
        video_repository = VideoRepository()
        section_repository = SectionRepository()
        count_repository = CountRepository()
        active_count = None

        self._model = Model(
            video_repository=video_repository,
            section_repository=section_repository,
            count_repository=count_repository,
            active_count=active_count,
        )

    def get(self) -> Model:
        return self._model
