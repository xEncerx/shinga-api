from sqlalchemy.exc import IntegrityError

from ...models import User, UserTitles
from ...session import get_session

from app.core import logger


class CreateOperations:
    @staticmethod
    async def user(user: User) -> bool:
        """Insert a user into the database."""
        async with get_session() as session:
            try:
                session.add(user)
                await session.commit()
                return True
            except IntegrityError:
                return False
            except Exception as e:
                logger.error(f"Failed to insert title: {e}")
                return False

    @staticmethod
    async def user_title(user_title: UserTitles) -> bool:
        """Insert or update a user title in the database."""
        async with get_session() as session:
            try:
                await session.merge(user_title)
                await session.commit()
                return True
            except Exception as e:
                logger.error(f"Failed to upsert user_title: {e}")
                return False
