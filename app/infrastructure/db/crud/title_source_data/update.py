from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import update

from app.infrastructure.db.models.title_source_data import TitleSourceData
from app.infrastructure.db.session import get_session
from app.domain.enums import ConsolidationStatus
from app.core import logger


class UpdateOperations:
    @staticmethod
    async def consolidation_status(
        session: AsyncSession,
        source_data_id: int,
        status: ConsolidationStatus,
        parse_error: str | None = None,
    ) -> TitleSourceData | None:
        """
        Update the consolidation status of a source.

        Args:
            session (AsyncSession): Async SQLModel session.
            source_data_id (int): TitleSourceData record ID.
            status (ConsolidationStatus): New consolidation status.
            parse_error (str | None): Optional error message. Defaults to None.

        Returns:
            TitleSourceData: Updated record.
        """
        try:
            source_data = await session.get(TitleSourceData, source_data_id)
            if not source_data:
                raise ValueError(f"TitleSourceData with id {source_data_id} not found")

            source_data.consolidation_status = status
            if parse_error is not None:
                source_data.parse_error = parse_error

            session.add(source_data)
            await session.commit()
            await session.refresh(source_data)

            return source_data
        except Exception as e:
            logger.error(
                f"Failed to update consolidation status for {source_data_id}: {e}",
                exc_info=True,
            )
            await session.rollback()

    @staticmethod
    async def all_stuck_in_progress() -> None:
        """
        Reset all IN_PROGRESS statuses to PENDING.
        """
        async with get_session() as session:
            try:
                stmt = (
                    update(TitleSourceData)
                    .where(TitleSourceData.consolidation_status == ConsolidationStatus.IN_PROGRESS)  # type: ignore
                    .values(consolidation_status=ConsolidationStatus.PENDING)
                )

                result = await session.exec(stmt)  # type: ignore
                await session.commit()

                updated_count = result.rowcount
                logger.info(
                    f"Reset {updated_count} stuck IN_PROGRESS records to PENDING"
                )
            except Exception as e:
                logger.error(f"Failed to reset stuck IN_PROGRESS: {e}", exc_info=True)
                await session.rollback()

    @staticmethod
    async def link_to_master_title(
        session: AsyncSession,
        source_data_id: int,
        master_title_id: int,
        auto_commit: bool = False,
    ) -> None:
        """
        Link source data to a master title.

        Args:
            session (AsyncSession): Async SQLModel session.
            source_data_id (int): TitleSourceData record ID.
            master_title_id (int): Master title ID.
            auto_commit (bool): Whether to commit the transaction automatically. Defaults to False.
        """
        source_data = await session.get(TitleSourceData, source_data_id)
        if not source_data:
            raise ValueError(f"TitleSourceData with id {source_data_id} not found")

        source_data.master_title_id = master_title_id
        source_data.consolidation_status = ConsolidationStatus.CONSOLIDATED
        session.add(source_data)

        if auto_commit:
            await session.commit()
