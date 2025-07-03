from sqlalchemy.exc import IntegrityError

from ...session import get_session
from ...models import Title

from app.core import logger

async def upsert_title(title: Title) -> bool:
    """Insert or update a title in the database."""
    async with get_session() as session:
        try:
            session.add(title)
            await session.commit()
            return True
        except IntegrityError:
            return True
        except Exception as e:
            logger.error(f"Failed to upsert title: {e}")
            return False

async def create_titles_bulk(titles: list[Title]) -> bool:
    """Create multiple titles in the database."""
    async with get_session() as session:
        try:
            session.add_all(titles)
            await session.commit()
            return True
        except IntegrityError:
            return True
        except Exception as e:
            logger.error(f"Failed to create titles: {e}")
            return False