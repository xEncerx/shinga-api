from sqlalchemy.dialects.postgresql import insert

from ...session import get_session
from ...models import Title

from app.core import logger

class CreateOperations:
    @staticmethod
    async def upsert(title: Title) -> bool:
        """Insert or update a title in the database."""
        async with get_session() as session:
            try:
                await session.merge(title)
                await session.commit()
                return True
            except Exception as e:
                logger.error(f"Failed to upsert title: {e}")
                return False
            
    @staticmethod
    async def bulk(titles: list[Title]) -> bool:
        """Create multiple titles in the database, ignoring duplicates."""
        async with get_session() as session:
            try:
                stmt = insert(Title).values([title.model_dump() for title in titles])
                stmt = stmt.on_conflict_do_nothing()
                await session.exec(stmt)  # type: ignore
                await session.commit()
                return True
            except Exception as e:
                logger.error(f"Failed to create titles: {e}")
                return False