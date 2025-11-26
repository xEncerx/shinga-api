from sqlmodel.ext.asyncio.session import AsyncSession
from abc import ABC, abstractmethod

from app.domain.models import TitleData, TitleMatchCandidate, MatchingStrategy
from app.infrastructure.db.models import Title, TitleSourceData
from app.domain.enums import SourceProvider
from app.core import logger


class BaseMatcher(ABC):
    """
    Base class for all matching strategies.

    Each matcher implements a specific strategy for finding duplicate titles.
    Matchers are executed in order of confidence (highest to lowest).
    """

    def __init__(self, session: AsyncSession):
        """
        Initialize matcher with database session.

        Args:
            session: Async SQLAlchemy|SQLModel session for database queries
        """
        self.session = session

    @abstractmethod
    async def find_matches(
        self,
        title_data: TitleData,
        limit: int = 5,
    ) -> list[TitleMatchCandidate]:
        """
        Find matching titles based on this strategy.

        Args:
            title_data: Parsed title data to match
            limit: Maximum number of candidates to return

        Returns:
            List of matching candidates sorted by confidence (highest first)
        """
        raise NotImplementedError("Subclasses must implement find_matches()")

    @abstractmethod
    def get_strategy_name(self) -> MatchingStrategy:
        """
        Return the name of this matching strategy.

        Returns:
            MatchingStrategy enum value
        """
        raise NotImplementedError("Subclasses must implement get_strategy_name()")

    @abstractmethod
    def get_min_confidence(self) -> float:
        """
        Return minimum confidence threshold for this strategy.

        Returns:
            Float between 0.0 and 1.0
        """
        raise NotImplementedError("Subclasses must implement get_min_confidence()")

    def _create_candidate(
        self,
        master_title_id: int,
        confidence: float,
        details: dict | None = None,
    ) -> TitleMatchCandidate:
        """
        Helper method to create a TitleMatchCandidate.

        Args:
            master_title_id: ID of the matched title
            confidence: Confidence score of the match (0.0 to 1.0)
            details: Optional dictionary with additional match details

        Returns:
            TitleMatchCandidate instance
        """
        return TitleMatchCandidate(
            master_title_id=master_title_id,
            confidence=confidence,
            strategy=self.get_strategy_name(),
            details=details,
        )
