from sqlmodel.ext.asyncio.session import AsyncSession
from typing import Optional

from app.domain.services.matching.multi_field_matcher import MultiFieldMatcher
from app.domain.services.matching.external_id_matcher import ExternalIdMatcher
from app.domain.services.matching.base_matcher import TitleMatchCandidate
from app.domain.models import TitleData
from app.core import logger


class MatchingResult:
    """Matching result."""

    def __init__(
        self,
        master_title_id: Optional[int],
        is_new_title: bool,
        primary_candidate: Optional[TitleMatchCandidate],
        all_candidates: list[TitleMatchCandidate],
    ):
        self.master_title_id = master_title_id
        self.is_new_title = is_new_title
        self.primary_candidate = primary_candidate
        self.all_candidates = all_candidates

    def is_high_confidence(self, threshold: float = 0.85) -> bool:
        """Check if confidence is high enough."""
        if not self.primary_candidate:
            return False
        return self.primary_candidate.confidence >= threshold


class MatchingEngine:
    """
    Main orchestrator for title matching.

    Coordinates different matchers in priority order:
    1. ExternalIdMatcher - matches by source_provider + source_id (highest confidence)
    2. MultiFieldMatcher - flexible matching using name + type + status + year + chapters/volumes with confidence-based scoring system

    Both matchers are designed to return high-confidence results (≥0.75-0.85).
    """

    # Matcher configuration in priority order
    MATCHER_PRIORITY = [
        ExternalIdMatcher,
        MultiFieldMatcher,
    ]

    def __init__(self, session: AsyncSession):
        """Initialize matching engine with database session."""
        self.matchers = [
            matcher_class(session) for matcher_class in self.MATCHER_PRIORITY
        ]

    async def find_match(
        self,
        title_data: TitleData,
        confidence_threshold: float = 0.85,
    ) -> MatchingResult:
        """
        Find match for title data.

        Strategy:
        1. Run matchers by priority until finding a candidate above threshold
        2. Return first high-confidence match
        3. If nothing found - mark as new title

        Args:
            title_data: Parsed title data for matching
            confidence_threshold: Minimum confidence for automatic match (default: 0.85)

        Returns:
            MatchingResult with match info or indication of new title
        """
        all_candidates = []

        for matcher in self.matchers:
            try:
                candidates = await matcher.find_matches(
                    title_data=title_data,
                    limit=5,
                )

                if not candidates:
                    continue

                logger.debug(
                    f"{matcher.get_strategy_name().value}: found {len(candidates)} candidates"
                )

                all_candidates.extend(candidates)

                # Check if best candidate meets threshold
                best_candidate = candidates[0]
                if best_candidate.confidence >= confidence_threshold:
                    logger.info(
                        f"Match found: master_id={best_candidate.master_title_id}, "
                        f"confidence={best_candidate.confidence:.2f}, "
                        f"strategy={best_candidate.strategy.value}"
                    )

                    return MatchingResult(
                        master_title_id=best_candidate.master_title_id,
                        is_new_title=False,
                        primary_candidate=best_candidate,
                        all_candidates=all_candidates,
                    )

            except Exception as e:
                logger.error(
                    f"Error in {matcher.get_strategy_name().value} matcher: {e}",
                    exc_info=True,
                )
                continue

        # No high-confidence match found
        if all_candidates:
            logger.debug(
                f"Found {len(all_candidates)} low-confidence candidates, "
                f"marking as new title"
            )
        else:
            logger.debug("No matching candidates found, title is new")

        return MatchingResult(
            master_title_id=None,
            is_new_title=True,
            primary_candidate=None,
            all_candidates=all_candidates,
        )
