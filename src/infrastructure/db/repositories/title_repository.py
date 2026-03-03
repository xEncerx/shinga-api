from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import update, select, func, text, and_
from datetime import datetime, timedelta, timezone
from contextlib import asynccontextmanager
from typing import AsyncGenerator
import hashlib

from src.infrastructure.db.models import (
    TitleRawDataDBModel,
    TitleDBModel,
    UserTitlesDBModel,
)
from src.domain.interfaces import ITitleRepository
from src.infrastructure.db.mappers import *
from src.domain.models import *


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
            .with_for_update(skip_locked=True)
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
        db_model = TitleDataMapper.to_db(
            domain_model=title_data.title_data,
            search_text=search_text,
            data_quality_score=data_quality_score,
            primary_source=title_data.source_metadata.source,
            extended_data=title_data.source_metadata.extended_data,
        )

        self._session.add(db_model)
        await self._session.flush()
        await self._session.refresh(db_model)

        return db_model.id  # type: ignore

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

    async def get_master_by_external_id(self, **external_id_field) -> TitleData | None:
        stmt = select(TitleDBModel).filter_by(**external_id_field)
        result = await self._session.exec(stmt)
        master_title = result.one_or_none()
        if not master_title:
            return None

        return TitleDataMapper.to_domain(master_title)

    async def get_master_by_name(
        self,
        normalized_name: str,
        limit: int = 20,
    ) -> list[TitleData]:
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
        return [TitleDataMapper.to_domain(i[0]) for i in result.all()]

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

    _SORT_COLUMN_MAP = {
        TitleSortBy.ID: TitleDBModel.id,
        TitleSortBy.RATING: TitleDBModel.rating,
        TitleSortBy.POPULARITY: TitleDBModel.popularity,
        TitleSortBy.CHAPTERS: TitleDBModel.chapters,
        TitleSortBy.VIEWS: TitleDBModel.views,
        TitleSortBy.FAVORITES: TitleDBModel.favorites,
        TitleSortBy.RELEASED_AT: TitleDBModel.released_at,
        TitleSortBy.UPDATED_AT: UserTitlesDBModel.updated_at,
    }

    async def search_titles(
        self,
        query: str | None = None,
        type: TitleType | None = None,
        status: TitleStatus | None = None,
        genres: list[str | TitleGenre] | None = None,
        categories: list[str | TitleCategory] | None = None,
        min_rating: float | None = None,
        max_rating: float | None = None,
        min_chapters: int | None = None,
        max_chapters: int | None = None,
        bookmark: TitleBookmark | None = None,
        user_id: int | None = None,
        sort_by: TitleSortBy = TitleSortBy.RATING,
        order: SortingOrder = SortingOrder.DESC,
        page: int = 1,
        page_size: int = 27,
    ) -> tuple[Pagination, list[tuple[TitleData, UserTitleData | None]]]:
        where_conditions = []
        tsquery = None

        # Window function — counts all matching rows without a second query
        total_count_col = func.count().over().label("total_count")

        # 1. Build base query depending on whether user_id is provided
        if user_id is not None:
            stmt = select(TitleDBModel, UserTitlesDBModel, total_count_col).outerjoin(
                UserTitlesDBModel,
                and_(
                    UserTitlesDBModel.title_id == TitleDBModel.id,  # type: ignore
                    UserTitlesDBModel.user_id == user_id,  # type: ignore
                ),
            )
        else:
            stmt = select(TitleDBModel, total_count_col)

        # 2. If a query is provided, perform a full-text search
        if query:
            tokens = query.strip().split()
            if tokens:
                tokens[-1] += ":*"
                tsquery_str = " & ".join(tokens)
                tsquery = func.to_tsquery("simple", tsquery_str)  # type: ignore
                where_conditions.append(
                    TitleDBModel.search_vector.op("@@")(tsquery)  # type: ignore
                )

        # 3. Filters by type, status, genres, categories, bookmark
        if type:
            where_conditions.append(TitleDBModel.type == type)
        if status:
            where_conditions.append(TitleDBModel.status == status)
        if genres:
            where_conditions.append(TitleDBModel.genres.contains(genres))  # type: ignore
        if categories:
            where_conditions.append(
                TitleDBModel.categories.contains(categories)  # type: ignore
            )
        if min_rating is not None:
            where_conditions.append(TitleDBModel.rating >= min_rating)
        if max_rating is not None:
            where_conditions.append(TitleDBModel.rating <= max_rating)
        if min_chapters is not None:
            where_conditions.append(TitleDBModel.chapters >= min_chapters)
        if max_chapters is not None:
            where_conditions.append(TitleDBModel.chapters <= max_chapters)

        if bookmark is not None and user_id is not None:
            where_conditions.append(UserTitlesDBModel.bookmark == bookmark)  # type: ignore

        # 4. Apply WHERE conditions
        if where_conditions:
            stmt = stmt.where(and_(*where_conditions))

        # 5. Sorting
        sort_column = self._SORT_COLUMN_MAP.get(sort_by, TitleDBModel.rating)
        if tsquery is not None:
            stmt = stmt.order_by(
                func.ts_rank(TitleDBModel.search_vector, tsquery).desc()
            )

        # If sorting by updated_at but we don't have user-specific data, sort by released_at instead
        if sort_column == TitleSortBy.UPDATED_AT and user_id is None:
            sort_column = TitleDBModel.released_at

        if order == SortingOrder.ASC:
            stmt = stmt.order_by(sort_column.asc())  # type: ignore
        else:
            stmt = stmt.order_by(sort_column.desc())  # type: ignore

        # 6. Pagination — single query with window function
        offset = (page - 1) * page_size
        stmt = stmt.offset(offset).limit(page_size)

        result = await self._session.exec(stmt)
        rows = result.all()

        total_count: int = 0
        content: list[tuple[TitleData, UserTitleData | None]] = []

        for row in rows:
            if user_id is not None:
                # row = (TitleDBModel, UserTitlesDBModel | None, total_count)
                title_row, user_title_row, total_count = row  # type: ignore
                user_title_data = (
                    UserTitleMapper.to_domain(user_title_row)  # type: ignore
                    if user_title_row is not None
                    else None
                )
            else:
                # row = (TitleDBModel, total_count)
                title_row, total_count = row  # type: ignore
                user_title_data = None

            title_data = TitleDataMapper.to_domain(title_row)  # type: ignore
            content.append((title_data, user_title_data))

        last_visible_page = (
            (total_count + page_size - 1) // page_size if total_count else 1
        )
        has_next_page = page < last_visible_page

        pagination = Pagination(
            last_visible_page=last_visible_page,
            has_next_page=has_next_page,
            current_page=page,
            items=PaginationItems(
                count=len(content),
                total=total_count,
                per_page=page_size,
            ),
        )

        return pagination, content

    async def reset_stuck_in_progress_statuses(
        self, stuck_threshold_minutes: int = 10 * 60
    ) -> None:
        cutoff_time = datetime.now(timezone.utc) - timedelta(
            minutes=stuck_threshold_minutes
        )

        stmt = (
            update(TitleRawDataDBModel)
            .where(
                and_(
                    TitleRawDataDBModel.consolidation_status
                    == ConsolidationStatus.IN_PROGRESS,
                    TitleRawDataDBModel.last_verified_at < cutoff_time,
                )
            )
            .values(
                consolidation_status=ConsolidationStatus.PENDING,
                consolidation_detail="Reset from stuck IN_PROGRESS status",
            )
        )

        await self._session.exec(stmt)
        await self._session.flush()

    @asynccontextmanager
    async def lock(self, key: str) -> AsyncGenerator[None, None]:
        """
        Acquire an advisory lock based on source and external_id.
        This ensures only one worker can upsert a specific title at a time.
        """
        key_hash = abs(int(hashlib.md5(key.encode()).hexdigest(), 16)) % (2**31)

        try:
            await self._session.exec(
                text("SELECT pg_advisory_xact_lock(:key)"),  # type: ignore
                params={"key": key_hash},
            )  # type: ignore
            yield
        finally:
            pass
