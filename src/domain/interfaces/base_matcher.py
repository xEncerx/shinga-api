from abc import ABC, abstractmethod

from src.domain.interfaces import ITitleRepository
from src.domain.models.titles import SourceTitleData, TitleData

__all__ = ["IBaseMatcher"]


class IBaseMatcher(ABC):
    """Base interface for matchers that find potential master titles for a given raw title."""

    def __init__(self, title_repo: ITitleRepository) -> None:
        self._title_repository = title_repo

    @property
    @abstractmethod
    def is_definitive(self) -> bool:
        """True if matcher provides 100% confidence"""
        raise NotImplementedError

    @abstractmethod
    async def find_candidates(self, raw_title: SourceTitleData) -> list[tuple[TitleData, int]]:
        """Returns list of master_title_ids with db id that are potential matches"""
        raise NotImplementedError
