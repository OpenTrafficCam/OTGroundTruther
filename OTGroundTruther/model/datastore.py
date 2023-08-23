from .count import ActiveCount, CountRepository
from .section import SectionRepository


class Datastore:
    """
    Central element to hold data in the application.
    """

    def __init__(
        self,
        section_repository: SectionRepository,
        count_repository: CountRepository,
        active_count: ActiveCount | None = None,
    ) -> None:
        self.section_repository = section_repository
        self.count_repository = count_repository

    def clear_repositories(self) -> None:
        self._event_repository.clear()
        self.section_repository.clear()
        self.count_repository.clear()
        self.active_count = None
