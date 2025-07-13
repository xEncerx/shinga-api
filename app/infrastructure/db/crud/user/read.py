from typing import Unpack, TypedDict
from sqlmodel import select, func

from app.domain.models.pagination import *
from ...session import get_session
from ...models import *

from app.core import logger

class _GetUserField(TypedDict, total=False):
    user_id: int | None
    username: str | None
    email: str | None
    yandex_id: str | None
    google_id: str | None


class ReadOperations:
    @staticmethod
    async def user(**kwargs: Unpack[_GetUserField]) -> User | None:
        """
        Gets a user by various identifiers.

        Args:
            user_id (int): The ID of the user.
            username (str): The username of the user.
            email (str): The email of the user.
            yandex_id (str): The Yandex ID of the user.
            google_id (str): The Google ID of the user.

        Returns:
            User | None: The user object if found, otherwise None.
        """
        async with get_session() as session:
            try:
                if user_id := kwargs.get("user_id"):
                    return await session.get(User, user_id)

                filters = {
                    k: v for k, v in kwargs.items() if v is not None
                }

                if not filters:
                    return None

                conditions = []
                for field, value in filters.items():
                    if field in ["username", "email"]:
                        conditions.append(func.lower(getattr(User, field)) == value.lower()) # type: ignore
                    else:
                        conditions.append(getattr(User, field) == value)

                result = await session.exec(select(User).where(conditions[0]))
                return result.first()

            except Exception as e:
                logger.error(f"Failed to get user: {e}")
                return None
    
    @staticmethod
    async def user_titles(
        username: str,
        page: int = 1,
        per_page: int = 10,
        bookmark: BookMarkType | None = None,
    ):
        """
        Gets titles associated with a user.

        Args:
            username (str): The username of the user.
            page (int): The page number for pagination.
            per_page (int): The number of items per page.
            bookmark (BookMarkType | None): The bookmark type to filter titles.

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

                # Base query
                stmt = (
                    select(Title, UserTitles)
                    .join(UserTitles, UserTitles.title_id == Title.id) # type: ignore
                    .where(UserTitles.username == username)
                    .order_by(UserTitles.updated_at.desc()) # type: ignore
                )

                if bookmark is not None:
                    stmt = stmt.where(UserTitles.bookmark == bookmark)

                count_stmt = select(func.count()).select_from(stmt.subquery())

                # Execute the count query
                total_count = (await session.exec(count_stmt)).first()
                total_count = total_count if total_count is not None else 0

                stmt = stmt.offset(offset).limit(per_page)
                data = await session.exec(stmt)
                rows = data.all()

                content = []
                for title, user_data in rows:
                    content.append(
                        {
                            "title": title.model_dump(),
                            "user_data": user_data.model_dump(),
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
                        )
                    ).model_dump(),
                    "content": content,
                }

            except Exception as e:
                logger.error(f"Failed to get user titles: {e}")
                return {
                    "pagination": Pagination().model_dump(),
                    "content": [],
                }