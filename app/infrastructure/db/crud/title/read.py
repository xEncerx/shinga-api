from sqlmodel import select, text, or_, and_
from sqlalchemy import func
from datetime import datetime, timedelta

from ...session import get_session
from ...models import *

from app.core import logger


async def get_title_by_id(id: str) -> Title | None:
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
                select(Title.id).where(Title.updated_at < now_time - time_ago),
            )
            return [i for i in result.all() if i is not None]
        except Exception as e:
            logger.error(f"Failed to fetch updatable titles: {e}")
            return []


async def search_titles_by_name(
    query: str,
    limit: int = 1,
) -> list[Title]:
    """
    Search for titles by their name using full-text search.

    Args:
        query (str): The search query string.
        limit (int): The maximum number of results to return.

    Returns:
        list[Title]: A list of Title objects that match the search query.
    """
    words = query.strip().split()
    if not words:
        return []

    async with get_session() as session:
        words[-1] = words[-1] + ":*"
        tsquery_str = " & ".join(words)
        tsquery = func.to_tsquery("russian", tsquery_str)

        statement = (
            select(Title)
            .where(Title.search_vector.op("@@")(tsquery))  # type: ignore
            .order_by(func.ts_rank(Title.search_vector, tsquery).desc())
            .limit(limit)
        )

        data = await session.exec(statement)
        return data.all()  # type: ignore
