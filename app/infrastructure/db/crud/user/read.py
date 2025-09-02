from sqlmodel import select, and_, func
from typing import TypedDict
import sys

if sys.version_info >= (3, 11):
    from typing import Unpack
else:
    from typing_extensions import Unpack

from app.domain.models.pagination import *
from ...session import get_session
from app.core import logger
from ...models import *


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

                filters = {k: v for k, v in kwargs.items() if v is not None}

                if not filters:
                    return None

                conditions = []
                for field, value in filters.items():
                    if field in ["username", "email"]:
                        conditions.append(func.lower(getattr(User, field)) == value.lower())  # type: ignore
                    else:
                        conditions.append(getattr(User, field) == value)

                result = await session.exec(select(User).where(conditions[0]))
                return result.first()

            except Exception as e:
                logger.error(f"Failed to get user: {e}")
                return None

    @staticmethod
    async def votes(username: str) -> UserVotes:
        """
        Get the voting statistics for a user.
        """
        async with get_session() as session:
            try:
                stmt = select(UserTitles.user_rating).where(
                    and_(
                        UserTitles.username == username,
                        UserTitles.user_rating > 0,
                    )
                )

                result = await session.exec(stmt)
                ratings = result.all()
                vote_counts = {i: 0 for i in range(1, 11)}
                total = len(ratings)

                for rating in ratings:
                    if 1 <= rating <= 10:
                        vote_counts[rating] += 1

                return UserVotes(
                    total=total,
                    vote_1=vote_counts[1],
                    vote_2=vote_counts[2],
                    vote_3=vote_counts[3],
                    vote_4=vote_counts[4],
                    vote_5=vote_counts[5],
                    vote_6=vote_counts[6],
                    vote_7=vote_counts[7],
                    vote_8=vote_counts[8],
                    vote_9=vote_counts[9],
                    vote_10=vote_counts[10],
                )
            except Exception as e:
                logger.error(f"Failed to get user votes: {e}")
                return UserVotes()
