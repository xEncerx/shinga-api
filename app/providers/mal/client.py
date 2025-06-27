from httpx import HTTPStatusError

from app.core import logger
from ..base_provider import BaseProvider, Title
from .parser import MalParser


class MalProvider(BaseProvider):
    """
    Provider for MyAnimeList (MAL) API.
    This class is responsible for interacting with the MAL API to fetch data.
    """

    def __init__(self, base_url="https://api.jikan.moe/v4/"):
        super().__init__(base_url=base_url)

    async def get_by_id(self, id: int, proxy: str | None = None) -> Title | int | None:  #type: ignore
        try:
            data = await self.get(url=f"manga/{id}", proxy=proxy)

            if not data: return

            return await MalParser.parse(data["data"])
        except HTTPStatusError as e:
            return e.response.status_code
        except Exception as e:
            logger.error(f"Error fetching data from MAL for ID {id}: {e}")
            return
