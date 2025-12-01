from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select

from app.infrastructure.db.models.title_source_data import TitleSourceData
from app.domain.enums import SourceProvider
from app.domain.models import TitleData


class CreateOperations:
    @classmethod
    async def title_source_data(
        cls,
        session: AsyncSession,
        source_provider: SourceProvider,
        source_id: str,
        title_data: TitleData,
        source_url: str | None = None,
    ) -> TitleSourceData:
        """
        Create a new raw source data record.

        Args:
            session (AsyncSession): Async SQLModel session.
            source_provider (SourceProvider): Source provider.
            source_id (str): ID on the source.
            title_data (TitleData): Parsed data for validation.
            source_url (str | None): URL on the source. Defaults to None.

        Returns:
            TitleSourceData: Created TitleSourceData record.
        """
        existing = await session.exec(
            select(TitleSourceData).where(
                (TitleSourceData.source_provider == source_provider)
                & (TitleSourceData.source_id == source_id)
            )
        )

        if existing.first():
            return await cls._update_title_source_data(
                session=session,
                source_provider=source_provider,
                source_id=source_id,
                title_data=title_data,
                source_url=source_url,
            )

        source_data = TitleSourceData(
            source_provider=source_provider,
            source_id=source_id,
            source_url=source_url,
            raw_data=title_data.to_raw_dict(),
            master_title_id=None,
        )

        session.add(source_data)
        await session.commit()
        await session.refresh(source_data)

        return source_data

    @classmethod
    async def _update_title_source_data(
        cls,
        session: AsyncSession,
        source_provider: SourceProvider,
        source_id: str,
        title_data: TitleData,
        source_url: str | None = None,
    ) -> TitleSourceData:
        """
        Update an existing raw data record.

        Args:
            session (AsyncSession): Async SQLModel session.
            source_provider (SourceProvider): Source provider.
            source_id (str): ID on the source.
            title_data (TitleData): New parsed data.
            source_url (str | None): New URL on the source. Defaults to None.

        Returns:
            TitleSourceData: Updated TitleSourceData record.
        """
        result = await session.exec(
            select(TitleSourceData).where(
                (TitleSourceData.source_provider == source_provider)
                & (TitleSourceData.source_id == source_id)
            )
        )

        source_data = result.first()
        if not source_data:
            raise ValueError(
                f"TitleSourceData not found for {source_provider}:{source_id}"
            )

        source_data.raw_data = title_data.to_raw_dict()
        source_data.source_url = source_url or source_data.source_url
        source_data.version += 1
        source_data.is_deleted_from_source = False  # Restore if was deleted

        session.add(source_data)
        await session.commit()
        await session.refresh(source_data)

        return source_data
