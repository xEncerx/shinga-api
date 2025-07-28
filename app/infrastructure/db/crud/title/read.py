from fastapi_cache.coder import PickleCoder
from fastapi_cache.decorator import cache

from sqlmodel import select, and_, desc, asc
from datetime import datetime, timedelta
from sqlalchemy import func

from app.domain.models.pagination import *
from ...session import get_session
from ...models import *

from app.core import logger


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
    async def search(
        query: str | None = None,
        genres: list[TitleGenre] | None = None,
        status: list[TitleStatus] | None = None,
        type_: list[TitleType] | None = None,
        min_rating: float | None = None,
        max_rating: float | None = None,
        min_chapters: int | None = None,
        max_chapters: int | None = None,
        sort_by: str = "rating",
        sort_order: str = "desc",
        page: int = 1,
        per_page: int = 21,
        username: str | None = None,
    ):
        """
        Advanced search with filters, sorting and pagination.

        Args:
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
            username (str | None): Username for user-specific data.

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

                stmt = select(Title, UserTitles).outerjoin(
                    UserTitles,
                    and_(
                        UserTitles.title_id == Title.id,
                        UserTitles.username == username,
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
                logger.error(f"Failed to get titles: {e}")
                return {
                    "pagination": Pagination().model_dump(),
                    "content": [],
                }
