from sqlmodel.ext.asyncio.session import AsyncSession

from app.domain.services.matching.matching_engine import MatchingEngine
from app.domain.services.consolidation.data_merger import DataMerger
from app.infrastructure.db.models.title.relations import TitleCover
from app.infrastructure.db.crud import TitleSourceDataCRUD
from app.domain.enums import ConsolidationStatus
from app.infrastructure.db.models import Title
from app.domain.models import TitleData
from app.core import logger


class ConsolidationService:
    """
    Service for consolidating and merging data from different sources.

    Orchestrates the process:
    1. Getting new source data
    2. Matching with existing titles
    3. Creating or updating master title
    4. Creating mappings between source_data and master_title
    5. Calculating data quality
    """

    def __init__(self, session: AsyncSession):
        """
        Initialize the consolidation service.

        Args:
            session: Async SQLModel session
        """
        self.session = session
        self.matcher = MatchingEngine(session)
        self.merger = DataMerger()

    async def consolidate_title(
        self,
        title_data: TitleData,
        source_data_id: int,
    ) -> tuple[bool, str]:
        """
        Consolidate one title from a source.

        Process:
        1. Perform matching
        2. If existing found - update it
        3. If new - create it
        4. Create mapping between source_data and master_title

        Args:
            title_data: Parsed data
            source_data_id: ID of TitleSourceData record

        Returns:
            Tuple (is_new, strategy_used)
        """
        # === Matching ===
        matching_result = await self.matcher.find_match(
            title_data=title_data,
            confidence_threshold=0.85,
        )

        # === If match exists ===
        if matching_result.master_title_id:
            existing_title = await self.session.get(
                Title,
                matching_result.master_title_id,
            )

            if not existing_title:
                logger.error(
                    f"Title with id {matching_result.master_title_id} not found"
                )
                raise ValueError("Matched title not found")

            # Merge data
            merged_title = self.merger.merge_sources(
                existing_title=existing_title,
                new_title_data=title_data,
            )

            # Update data_quality_score
            merged_title.data_quality_score = self.merger.calculate_data_quality_score(
                merged_title
            )

            self.session.add(merged_title)

            # Link source_data with master_title
            await TitleSourceDataCRUD.update.link_to_master_title(
                session=self.session,
                source_data_id=source_data_id,
                master_title_id=merged_title.id,  # type: ignore
            )

            await self.session.commit()

            logger.info(
                f"Consolidated title (UPDATED): {merged_title.name_en or merged_title.name_ru} (id={merged_title.id}, source_data_id={source_data_id})"
            )

            return (
                False,
                matching_result.primary_candidate.strategy.value,
            )

        # === New title ===
        else:
            # Create new master title
            new_title = Title(**title_data.to_title_dict())

            # Set placeholder cover for now
            new_title.cover = TitleCover.pending_placeholder()

            # Set primary source
            new_title.primary_source = title_data.source_provider

            # Calculate quality score
            new_title.data_quality_score = self.merger.calculate_data_quality_score(
                new_title
            )

            self.session.add(new_title)
            await self.session.flush()

            # Link source_data with new master_title
            await TitleSourceDataCRUD.update.link_to_master_title(
                session=self.session,
                source_data_id=source_data_id,
                master_title_id=new_title.id,  # type: ignore
            )

            await self.session.commit()

            # Create task for downloading covers
            self.merger.download_covers(
                title_id=new_title.id,
                cover_url=title_data.cover.url,  # type: ignore
                source_provider=title_data.source_provider,
            )

            logger.info(
                f"Consolidated title (NEW): {new_title.name_en or new_title.name_ru} (id={new_title.id}, source_data_id={source_data_id})"
            )

            return (True, "NEW_TITLE")

    async def consolidate_batch(
        self,
        title_data_list: list[tuple[TitleData, int]],
    ) -> dict:
        """
        Consolidate a batch of titles.

        Args:
            title_data_list: List of tuples (title_data, source_data_id)

        Returns:
            Dictionary with statistics
        """
        stats = {
            "total": len(title_data_list),
            "consolidated": 0,
            "updated": 0,
            "new": 0,
            "errors": 0,
        }

        for title_data, source_data_id in title_data_list:
            try:
                is_new, _ = await self.consolidate_title(
                    title_data=title_data,
                    source_data_id=source_data_id,
                )

                stats["consolidated"] += 1
                if is_new:
                    stats["new"] += 1
                else:
                    stats["updated"] += 1

            except Exception as e:
                stats["errors"] += 1
                logger.error(f"Error consolidating title: {e}", exc_info=True)

                await self.session.rollback()

                await TitleSourceDataCRUD.update.consolidation_status(
                    session=self.session,
                    source_data_id=source_data_id,
                    status=ConsolidationStatus.FAILED,
                    parse_error=str(e)[:500],
                )

                continue

        logger.info(f"Batch consolidation complete: {stats}")
        return stats
