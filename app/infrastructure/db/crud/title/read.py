from sqlmodel import select, func, and_, text, or_
from datetime import datetime, timedelta

from ...session import get_session
from ...models import *

from app.core import logger


async def get_last_id() -> int:
    """Fetch the last ID from the Titles table."""
    async with get_session() as session:
        try:
            result = await session.exec(select(func.max(Title.id)))
            last_id = result.first()
            return last_id if last_id is not None else 0
        except Exception as e:
            logger.error(f"Failed to get last title ID: {e}")
            return 0


async def get_title_by_id(id: int) -> Title | None:
    """Fetch a title by its ID."""
    async with get_session() as session:
        try:
            result = await session.exec(select(Title).where(Title.id == id))
            return result.first()
        except:
            return None


async def get_titles_for_update(time_ago: timedelta) -> list[str]:
    """Fetch all titles that need to be updated."""
    async with get_session() as session:
        try:
            now_time = datetime.now()
            result = await session.exec(
                select(Title.id).where(
                    and_(
                        Title.status != TitleStatus.FINISHED,
                        Title.updated_at < now_time - time_ago,
                        Title.source_provider == SourceProvider.MAL,
                    )
                ),
            )
            return [i for i in result.all() if i is not None]
        except Exception as e:
            logger.error(f"Failed to fetch updatable titles: {e}")
            return []


async def get_titles_for_translation() -> list[str]:
    """Fetch all titles that need to translate"""
    async with get_session() as session:
        try:
            result = await session.exec(
                select(Title.id).where(
                    and_(
                        or_(
                            Title.name_ru == None,
                            text("description->>'ru' IS NULL"),
                        ),
                        Title.source_provider == SourceProvider.MAL,
                    )
                ).order_by(Title.popularity.asc()) # type: ignore
            )
            return [i for i in result.all() if i is not None]
        except Exception as e:
            logger.error(f"Failed to fetch titles for translation: {e}")
            return []
