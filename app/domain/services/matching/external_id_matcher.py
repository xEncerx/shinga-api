from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import select, and_, func

from app.domain.services.matching.base_matcher import *
from app.core import logger


class ExternalIdMatcher(BaseMatcher):
    """
    Matcher by external IDs.

    Used to find duplicates using common IDs from different sources.
    
    For example, MAL ID is used by both Shikimori and other services.

    This is the HIGHEST confidence matching strategy.
    """

    async def find_matches(
        self,
        title_data: TitleData,
        limit: int = 5,
    ) -> list[TitleMatchCandidate]:
        """
        Find matches by external IDs.

        Args:
            title_data (TitleData): Parsed data.
            limit (int): Maximum number of candidates. Defaults to 5.

        Returns:
            list[TitleMatchCandidate]: List of candidates.
        """
        candidates = []

        # Search by MAL ID if available
        if title_data.mal_id:
            mal_candidates = await self._find_by_mal_id(
                title_data.mal_id,
                limit=limit,
            )
            candidates.extend(mal_candidates)

        if candidates:
            return candidates

        return []

    async def _find_by_mal_id(
        self,
        mal_id: int,
        limit: int = 5,
    ) -> list[TitleMatchCandidate]:
        """
        Find by MAL ID.

        Strategy:
        1. Search source data (TitleSourceData) with the same mal_id in raw_data
        2. If found, take their master_title_id
        3. Return as candidates with maximum confidence

        Args:
            mal_id (int): MyAnimeList ID.
            limit (int): Maximum number of results. Defaults to 5.

        Returns:
            list[TitleMatchCandidate]: List of candidates.
        """
        try:
            query = (
                select(TitleSourceData)
                .distinct(TitleSourceData.master_title_id)  # type: ignore
                .where(
                    and_(
                        TitleSourceData.raw_data.op("@>")(  # type: ignore
                            func.cast({"mal_id": mal_id}, JSONB)  # type: ignore
                        ),
                        TitleSourceData.master_title_id.isnot(None),  # type: ignore
                    )
                )
                .order_by(
                    TitleSourceData.master_title_id,  # type: ignore
                    TitleSourceData.fetched_at.desc(),  # type: ignore
                )
                .limit(limit)
            )

            result = await self.session.exec(query)
            source_data_list = result.all()

            candidates = []
            for source_data in source_data_list:
                candidate = self._create_candidate(
                    master_title_id=source_data.master_title_id,  # type: ignore
                    confidence=1.0,
                    details={
                        "mal_id": mal_id,
                        "source_provider": source_data.source_provider.value,
                        "matched_field": "mal_id",
                    },
                )
                candidates.append(candidate)

            logger.info(
                f"ExternalIdMatcher: Found {len(candidates)} candidates "
                f"for mal_id={mal_id}"
            )
            return candidates

        except Exception as e:
            logger.error(f"ExternalIdMatcher error searching by mal_id: {e}", exc_info=True)
            return []

    def get_strategy_name(self) -> MatchingStrategy:
        """Get strategy name."""
        return MatchingStrategy.EXTERNAL_ID

    def get_min_confidence(self) -> float:
        """Minimum confidence for this strategy."""
        return 0.95  # Very strict requirement for external IDs
