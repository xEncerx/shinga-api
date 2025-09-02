from fastapi_cache.coder import PickleCoder
from fastapi_cache.decorator import cache

from datetime import datetime, timedelta
from sqlmodel import select

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
