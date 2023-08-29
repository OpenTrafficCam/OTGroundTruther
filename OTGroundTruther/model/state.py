from OTGroundTruther.model.model import Model


class RepositoryState:
    def __init__(self, model: Model) -> None:
        self._model = model

    def videos_in_repository(self) -> bool:
        return self._model._video_repository.is_empty()

    def sections_in_repository(self) -> bool:
        return not self._model._section_repository.is_empty()

    def counts_in_repository(self) -> bool:
        return not self._model._count_repository.is_empty()
