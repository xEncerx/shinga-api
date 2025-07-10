from sqlalchemy.exc import IntegrityError

from ...models import User, UserTitles
from ...session import get_session

from app.core import logger


async def persist_user(user: User) -> bool:
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
