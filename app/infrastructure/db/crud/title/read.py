from fastapi_cache.coder import PickleCoder
from fastapi_cache.decorator import cache

from sqlmodel import select, and_, desc, asc, func, or_, case
from datetime import datetime, timedelta
from typing import Any

from app.domain.models import *
from ...session import get_session
from ...models import *

from app.core import logger


class TitleSearchMode(str, Enum):
    GLOBAL = "global"
    USER_ONLY = "user_only"


class ReadOperations:
    @staticmethod
    @cache(expire=30 * 60, coder=PickleCoder)
    async def by_id(id: str) -> Title | None:
        """Fetch a title by its ID."""
        async with get_session() as session:
            try:
                result = await session.exec(select(Title).where(Title.id == id))
                return result.first()
            except:
                return None

    @staticmethod
    async def for_update(time_ago: timedelta) -> list[str]:
        """Fetch all titles that need to be updated."""
        async with get_session() as session:
            try:
                now_time = datetime.now()
                result = await session.exec(
                    select(Title.id).where(Title.updated_at < now_time - time_ago),
                )
                return [i for i in result.all() if i is not None]
            except Exception as e:
                logger.error(f"Failed to fetch updatable titles: {e}")
                return []

    @staticmethod
    async def with_user_data(
        title_id: str,
        user_id: int | None,
    ) -> dict[str, Any] | None:
        """
        Fetch title and user-specific data.

        Args:
            title_id (str): The ID of the title to fetch.
            user_id (int | None): The user ID for user-specific data.

        Returns:
            A dictionary formatted as follows
            ```
            {
                "title": {Title as dict} | None,
                "user_data": {UserTitles as dict} | None
            }
            Or None if title not found.
            ```
        """
        async with get_session() as session:
            try:
                stmt = (
                    select(Title, UserTitles)
                    .outerjoin(
                        UserTitles,
                        and_(
                            UserTitles.title_id == Title.id,
                            UserTitles.user_id == user_id,
                        ),
                    )
                    .where(Title.id == title_id)
                ).limit(1)

                result = await session.exec(stmt)
                title = result.first()
                if title:
                    return {
                        "title": title[0].model_dump(),
                        "user_data": title[1].model_dump() if title[1] else None,
                    }
            except Exception as e:
                logger.error(f"Failed to fetch title with user data: {e}")

    @staticmethod
    async def search(
        mode: TitleSearchMode,
        query: str | None = None,
        genres: list[TitleGenre] | None = None,
        status: list[TitleStatus] | None = None,
        type_: list[TitleType] | None = None,
        min_rating: float | None = None,
        max_rating: float | None = None,
        min_chapters: int | None = None,
        max_chapters: int | None = None,
        sort_by: str = TitleSortBy.rating,
        sort_order: str = TitleSortOrder.desc,
        page: int = 1,
        per_page: int = 21,
        bookmark: BookMarkType | None = None,
        user_id: int | None = None,
    ) -> dict[str, Any]:
        """
        Advanced search with filters, sorting and pagination.

        Args:
            mode (TitleSearchMode): Search mode (global or user_only).
            query (str | None): Search query for title names.
            genres (list[TitleGenre] | None): List of genres to filter by.
            status (list[TitleStatus] | None): List of statuses to filter by.
            type_ (list[TitleType] | None): List of types to filter by.
            min_rating (float | None): Minimum rating to filter by.
            max_rating (float | None): Maximum rating to filter by.
            min_chapters (int | None): Minimum chapters to filter by.
            max_chapters (int | None): Maximum chapters to filter by.
            sort_by (str): Column to sort by.
            sort_order (str): Order to sort (asc/desc).
            page (int): Page number for pagination.
            per_page (int): Number of results per page.
            bookmark (BookMarkType | None): Bookmark for pagination.
            user_id (int | None): User ID for user-specific data.

        Returns:
            A dictionary formatted as follows
            ```
            {
                "pagination": Pagination as dict,
                "content": list[
                    {
                    "title": {Title as dict},
                    "user_data": {UserTitles as dict}
                    }
                ]
            }
            ```
        """
        async with get_session() as session:
            try:
                offset = (page - 1) * per_page

                # Base statement
                if mode == TitleSearchMode.USER_ONLY:
                    stmt = (
                        select(Title, UserTitles)
                        .join(UserTitles, UserTitles.title_id == Title.id)  # type: ignore
                        .where(UserTitles.user_id == user_id)
                    )
                else:
                    stmt = select(Title, UserTitles).outerjoin(
                        UserTitles,
                        and_(
                            UserTitles.title_id == Title.id,
                            UserTitles.user_id == user_id,
                        ),
                    )

                conditions = []
                tsquery = None

                # Search by title name
                if query:
                    words = query.strip().split()
                    if words:
                        words[-1] = words[-1] + ":*"
                        tsquery_str = " & ".join(words)
                        tsquery = func.to_tsquery("russian", tsquery_str)
                        conditions.append(Title.search_vector.op("@@")(tsquery))  # type: ignore

                # Filter by genres
                if genres:
                    conditions.append(Title.genres.op("@>")(set(genres)))  # type: ignore

                # Filter by status
                if status:
                    conditions.append(Title.status.in_(set(status)))  # type: ignore

                # Filter by type
                if type_:
                    conditions.append(Title.type_.in_(set(type_)))  # type: ignore

                # Filter by rating
                if min_rating is not None:
                    conditions.append(Title.rating >= min_rating)
                if max_rating is not None:
                    conditions.append(Title.rating <= max_rating)

                # Filter by chapters
                if min_chapters is not None:
                    conditions.append(Title.chapters >= min_chapters)
                if max_chapters is not None:
                    conditions.append(Title.chapters <= max_chapters)

                # Filter by bookmark
                if bookmark:
                    conditions.append(UserTitles.bookmark == bookmark)

                # Apply the filters
                if conditions:
                    stmt = stmt.where(and_(*conditions))

                # Sorting
                # - Sort by name relevance
                if tsquery is not None:
                    stmt = stmt.order_by(
                        func.ts_rank(Title.search_vector, tsquery).desc()
                    )

                # - Sort by other columns
                if sort_by is TitleSortBy.user_updated_at:
                    sort_column = UserTitles.updated_at
                else:
                    sort_column = getattr(Title, sort_by, Title.rating)

                if sort_order.lower() == "desc":
                    stmt = stmt.order_by(desc(sort_column))
                else:
                    stmt = stmt.order_by(asc(sort_column))

                # Pagination
                count_stmt = select(func.count()).select_from(stmt.subquery())
                total_count = (await session.exec(count_stmt)).first() or 0
                stmt = stmt.offset(offset).limit(per_page)

                data = await session.exec(stmt)
                rows = data.all()

                content = []
                for title, user_titles in rows:
                    content.append(
                        {
                            "title": title.model_dump(),
                            "user_data": (
                                user_titles.model_dump() if user_titles else None
                            ),
                        }
                    )

                last_visible_page = (total_count + per_page - 1) // per_page
                has_next_page = page < last_visible_page

                return {
                    "pagination": Pagination(
                        last_visible_page=last_visible_page,
                        has_next_page=has_next_page,
                        current_page=page,
                        items=PaginationItems(
                            count=len(content),
                            total=total_count,
                            per_page=per_page,
                        ),
                    ).model_dump(),
                    "content": content,
                }
            except Exception as e:
                logger.error(f"TitleCRUD.search failed: {e}")
                return {
                    "pagination": Pagination(),
                    "content": [],
                }

    @staticmethod
    async def recommendations(
        title_id: str,
        user_id: int | None = None,
        limit: int = 20,
    ) -> dict[str, Any]:
        """
        Get recommendations for a title based on user preferences.
        Based on genre, type, rating similarity and popularity.

        Args:
            title_id (str): The ID of the source title.
            user_id (int | None): The user ID for user-specific data.
            limit (int): Number of recommendations to return.

        Returns:
            A dictionary formatted as follows
            ```
            {
                "content": list[
                    {
                    "title": {Title as dict},
                    "user_data": {UserTitles as dict}
                    }
                ]
            }
            ```
        """
        async with get_session() as session:
            try:
                source_stmt = select(Title).where(Title.id == title_id)
                source_result = await session.exec(source_stmt)
                source_title = source_result.first()

                if not source_title:
                    return {"content": []}

                # Build recommendation query
                # Priority: Same genres > Same type > Similar rating
                base_stmt = (
                    select(Title, UserTitles)
                    .outerjoin(
                        UserTitles,
                        and_(
                            UserTitles.title_id == Title.id,
                            UserTitles.user_id == user_id,
                        ),
                    )
                    .where(
                        and_(
                            Title.id != title_id,  # Exclude source title
                            Title.rating >= 4.0,  # Quality filter
                            or_(
                                # Same genres (highest priority)
                                Title.genres.op("@>")(source_title.genres[:3]) if source_title.genres else False,  # type: ignore
                                # Same type (medium priority)
                                Title.type_ == source_title.type_,
                                # Similar rating range (low priority)
                                and_(
                                    Title.rating >= source_title.rating - 1.5,
                                    Title.rating <= source_title.rating + 1.5,
                                    Title.genres.op("&&")(source_title.genres) if source_title.genres else False,  # type: ignore
                                ),
                            ),
                        )
                    )
                    .order_by(
                        # Sort by relevance: genre overlap, rating, popularity
                        desc(
                            case(
                                (Title.genres.op("@>")(source_title.genres[:2]) if source_title.genres else False, 3),  # type: ignore
                                (Title.type_ == source_title.type_, 2),
                                else_=1,
                            )
                        ),
                        desc(Title.rating),
                        desc(Title.popularity),
                    )
                    .limit(limit)
                )

                result = await session.exec(base_stmt)
                rows = result.all()

                content = []
                for title, user_data in rows:
                    content.append(
                        {
                            "title": title.model_dump(),
                            "user_data": user_data.model_dump() if user_data else None,
                        }
                    )

                return {"content": content}

            except Exception as e:
                logger.error(f"TitleCRUD.recommendations failed: {e}")
                return {"content": []}
