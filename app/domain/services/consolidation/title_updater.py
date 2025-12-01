from sqlmodel.ext.asyncio.session import AsyncSession

from app.domain.services.consolidation.data_merger import DataMerger
from app.infrastructure.db.crud import TitleSourceDataCRUD
from app.infrastructure.db.models import Title
from app.domain.models import TitleData
from app.core import logger


class TitleUpdateService:
    """
    Service for updating existing master titles based on all their sources.

    Responsible for:
    1. Fetching all source data for a master title
    2. Merging data from all sources
    3. Recalculating data quality score
    4. Updating the master title
    """

    def __init__(self, session: AsyncSession):
        """
        Initialize the title update service.

        Args:
            session: Async SQLModel session
        """
        self.session = session
        self.merger = DataMerger()

    async def update_title(
        self,
        master_title_id: int,
    ) -> bool:
        """
        Update master title based on all its sources.

        Fetches all source_data for the title and merges all data.

        Args:
            master_title_id: ID of master title to update

        Returns:
            bool: True if the title was successfully updated, False otherwise
        """
        try:
            # Get existing master title
            existing_title = await self.session.get(
                Title,
                master_title_id,
            )

            if not existing_title:
                logger.error(f"Master title {master_title_id} not found")
                return False

            all_sources = await TitleSourceDataCRUD.read.all_sources_for_title(
                session=self.session,
                master_title_id=master_title_id,
            )

            if not all_sources:
                logger.warning(f"No sources found for title {master_title_id}")
                return False

            # Merge data
            merged_title = existing_title

            for source_data in all_sources:
                try:
                    title_data = TitleData.from_raw_dict(source_data.raw_data)

                    # Gradually merge data from each source
                    merged_title = await self.merger.merge_sources(
                        existing_title=merged_title,
                        new_title_data=title_data,
                    )
                except Exception as e:
                    logger.error(
                        f"Error parsing source_data {source_data.id}: {e}",
                        exc_info=True,
                    )
                    continue

            # Update data_quality_score
            merged_title.data_quality_score = self.merger.calculate_data_quality_score(
                merged_title
            )

            self.session.add(merged_title)
            await self.session.commit()
            await self.session.refresh(merged_title)

            logger.info(
                f"Updated title: {merged_title.name_en or merged_title.name_ru} (id={merged_title.id}, from {len(all_sources)} sources)"
            )

            return True

        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error updating title {master_title_id}: {e}", exc_info=True)
            return False
