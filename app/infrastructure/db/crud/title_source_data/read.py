from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, update, and_
from typing import Optional

from app.infrastructure.db.models.title_source_data import TitleSourceData
from app.domain.enums import ConsolidationStatus, SourceProvider


class ReadOperations:
    @staticmethod
    async def source_data_by_id(
        session: AsyncSession,
        id: int,
    ) -> Optional[TitleSourceData]:
        """
        Get source record by ID.

        Args:
            session (AsyncSession): Async SQLModel session.
            id (int): Record ID.

        Returns:
            Optional[TitleSourceData]: TitleSourceData or None.
        """
        return await session.get(TitleSourceData, id)

    @staticmethod
    async def claim_unmapped_ids(
        session: AsyncSession,
        fetch_size: int = 100,
        source_provider: Optional[SourceProvider] = None,
    ) -> list[int]:
        """
        Fetch and unmapped source IDs and set consolidation status to IN_PROGRESS.

        Args:
            session (AsyncSession): Async SQLModel session.
            fetch_size (int): Maximum number of records. Defaults to 100.
            source_provider (Optional[SourceProvider]): Provider filter (optional). Defaults to None.

        Returns:
            list[int]: List of unmapped TitleSourceData IDs.
        """
        select_query = (
            select(TitleSourceData.id)
            .where(TitleSourceData.consolidation_status == ConsolidationStatus.PENDING)
            .order_by(TitleSourceData.fetched_at)  # type: ignore
            .limit(fetch_size)
        )

        if source_provider:
            select_query = select_query.where(
                TitleSourceData.source_provider == source_provider
            )

        result = await session.exec(select_query)
        ids = [i for i in result.all() if i is not None]

        if not ids:
            return []

        update_query = (
            update(TitleSourceData)
            .where(
                and_(
                    TitleSourceData.id.in_(ids),  # type: ignore
                    TitleSourceData.consolidation_status == ConsolidationStatus.PENDING,
                )
            )
            .values(consolidation_status=ConsolidationStatus.IN_PROGRESS)
        )

        await session.exec(update_query)  # type: ignore
        await session.commit()

        return ids

    @staticmethod
    async def all_sources_for_title(
        session: AsyncSession,
        master_title_id: int,
    ) -> list[TitleSourceData]:
        """
        Get all sources for a master title.

        Args:
            session (AsyncSession): Async SQLModel session.
            master_title_id (int): Master title ID.

        Returns:
            list[TitleSourceData]: List of all TitleSourceData for this title.
        """
        query = (
            select(TitleSourceData)
            .where(
                TitleSourceData.master_title_id == master_title_id,
                TitleSourceData.is_deleted_from_source.is_(False),  # type: ignore
            )
            .order_by(TitleSourceData.last_verified_at.desc())  # type: ignore
        )

        result = await session.exec(query)

        return [i for i in result.all()]
