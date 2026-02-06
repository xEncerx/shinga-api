from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import update, select, func, text, and_
from datetime import datetime, timedelta, timezone

from src.domain.models.titles import (
    SourceTitleData,
    TitleData,
    TitleCover,
)
from src.infrastructure.db.models import TitleRawDataDBModel, TitleDBModel
from src.domain.models.services.enums import ConsolidationStatus
from src.domain.interfaces import ITitleRepository
from src.infrastructure.db.mappers import *


class TitleRepository(ITitleRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def upsert_raw_title(
        self,
        raw_title: SourceTitleData,
    ) -> int | None:
        insert_values = SourceTitleDataMapper.to_db_dict(raw_title)

        stmt = pg_insert(TitleRawDataDBModel).values(**insert_values)
        stmt = stmt.on_conflict_do_update(
            constraint="uq_source_external_id",
            set_={
                "is_deleted": stmt.excluded.is_deleted,
                "raw_data": stmt.excluded.raw_data,
                "extended_data": stmt.excluded.extended_data,
                "source_url": stmt.excluded.source_url,
                "last_verified_at": stmt.excluded.last_verified_at,
            },
        ).returning(
            TitleRawDataDBModel.id  # type: ignore
        )  # type: ignore

        result = await self._session.exec(stmt)
        await self._session.flush()

        return result.scalar_one_or_none()

    async def get_raw_title(self, raw_title_id: int) -> SourceTitleData | None:
        result = await self._session.get(TitleRawDataDBModel, raw_title_id)
        if not result:
            return None

        return SourceTitleDataMapper.to_domain(result)

    async def get_unmapped_raw_titles(self, limit: int) -> list[int]:
        stmt = (
            select(TitleRawDataDBModel.id)
            .where(
                and_(
                    TitleRawDataDBModel.consolidation_status
                    == ConsolidationStatus.PENDING,
                    TitleRawDataDBModel.is_deleted == False,
                )
            )
            .limit(limit)
        )

        result = await self._session.exec(stmt)
        ids = [i for i in result.all() if i is not None]
        if not ids:
            return []

        update_stmt = (
            update(TitleRawDataDBModel)
            .where(
                and_(
                    TitleRawDataDBModel.id.in_(ids),  # type: ignore
                    TitleRawDataDBModel.consolidation_status
                    == ConsolidationStatus.PENDING,
                )
            )
            .values(consolidation_status=ConsolidationStatus.IN_PROGRESS)
        )
        await self._session.exec(update_stmt)
        await self._session.flush()

        return ids

    async def update_consolidation_status(
        self,
        raw_title_id: int,
        status: ConsolidationStatus,
        detail: str | None = None,
    ) -> None:
        stmt = (
            update(TitleRawDataDBModel)
            .where(TitleRawDataDBModel.id == raw_title_id)  # type: ignore
            .values(
                consolidation_status=status,
                consolidation_detail=detail,
            )
        )
        await self._session.exec(stmt)
        await self._session.flush()

    async def link_raw_to_master(self, raw_title_id: int, master_title_id: int) -> None:
        stmt = (
            update(TitleRawDataDBModel)
            .where(TitleRawDataDBModel.id == raw_title_id)  # type: ignore
            .values(master_title_id=master_title_id)
        )
        await self._session.exec(stmt)
        await self._session.flush()

    async def add_master_title(
        self,
        title_data: SourceTitleData,
        search_text: str,
        data_quality_score: float,
    ) -> int:
        master_title = TitleDataMapper.to_db(
            domain_model=title_data.title_data,
            search_text=search_text,
            data_quality_score=data_quality_score,
            primary_source=title_data.source_metadata.source,
            extended_data=title_data.source_metadata.extended_data,
        )

        self._session.add(master_title)
        await self._session.flush()
        await self._session.refresh(master_title)

        return master_title.id  # type: ignore

    async def get_master_title(self, master_title_id: int) -> TitleData | None:
        result = await self._session.get(TitleDBModel, master_title_id)
        if not result:
            return None

        return TitleDataMapper.to_domain(result)

    async def get_master_title_for_update(
        self,
        hours: int = 168,
        limit: int = 100,
        last_id: int = 0,
    ) -> list[int]:
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)

        stmt = (
            select(TitleDBModel.id)
            .join(
                TitleRawDataDBModel,
                TitleRawDataDBModel.master_title_id == TitleDBModel.id,  # type: ignore
            )
            .where(
                TitleRawDataDBModel.last_verified_at >= cutoff_time,
                TitleRawDataDBModel.is_deleted == False,
                TitleDBModel.updated_at < TitleRawDataDBModel.last_verified_at,
                TitleDBModel.id > last_id,  # type: ignore
            )
            .distinct()
            .limit(limit)
        )

        result = await self._session.exec(stmt)
        return [i for i in result.all() if i is not None]

    async def get_raw_titles_by_master_id(
        self, master_title_id: int
    ) -> list[TitleData]:
        stmt = select(TitleRawDataDBModel).where(
            TitleRawDataDBModel.master_title_id == master_title_id
        )
        result = await self._session.exec(stmt)
        raw_titles = result.all()

        titles = [
            TitleDataMapper.to_domain(raw_title.raw_data) for raw_title in raw_titles
        ]
        return titles

    async def update_master_title(
        self,
        master_title_id: int,
        title_data: TitleData,
        search_text: str,
        data_quality_score: float,
    ) -> None:
        stmt = (
            update(TitleDBModel)
            .where(TitleDBModel.id == master_title_id)  # type: ignore
            .values(
                mal_id=title_data.mal_id,
                name_ru=title_data.name_ru,
                name_en=title_data.name_en,
                alt_names=title_data.alt_names,
                description_ru=title_data.description_ru,
                description_en=title_data.description_en,
                popularity=title_data.popularity,
                rating=title_data.rating,
                scored_by=title_data.scored_by,
                chapters=title_data.chapters,
                volumes=title_data.volumes,
                views=title_data.views,
                favorites=title_data.favorites,
                genres=title_data.genres,
                categories=title_data.categories,
                authors=title_data.authors,
                released_at=title_data.released_at,
                ended_at=title_data.ended_at,
                type=title_data.type,
                status=title_data.status,
                # Update calculated fields
                search_text=search_text,
                data_quality_score=data_quality_score,
            )
        )
        await self._session.exec(stmt)
        await self._session.flush()

    async def get_master_by_external_id(
        self, **external_id_field
    ) -> tuple[TitleData, int] | None:
        stmt = select(TitleDBModel).filter_by(**external_id_field)
        result = await self._session.exec(stmt)
        master_title = result.one_or_none()
        if not master_title:
            return None

        return (TitleDataMapper.to_domain(master_title), master_title.id)  # type: ignore

    async def get_master_by_name(
        self,
        normalized_name: str,
        limit: int = 20,
    ) -> list[tuple[TitleData, int]]:
        tokens = normalized_name.split()
        if not tokens:
            return []

        tsquery = " | ".join(tokens)
        stmt = (
            select(
                TitleDBModel,
                func.ts_rank(
                    TitleDBModel.search_vector,
                    func.to_tsquery("simple", tsquery),
                ).label("rank"),
            )
            .where(
                TitleDBModel.search_vector.op("@@")(func.to_tsquery("simple", tsquery))  # type: ignore
            )
            .order_by(text("rank DESC"))
            .limit(limit)
        )

        result = await self._session.exec(stmt)
        return [
            (TitleDataMapper.to_domain(i[0]), i[0].id) for i in result.all()
        ]  # type: ignore

    async def update_master_title_cover(
        self,
        master_title_id: int,
        cover: TitleCover,
    ) -> None:
        stmt = (
            update(TitleDBModel)
            .where(TitleDBModel.id == master_title_id)  # type: ignore
            .values(cover=cover)
        )
        await self._session.exec(stmt)
        await self._session.flush()
