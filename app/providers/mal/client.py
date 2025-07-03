from aiohttp.client_exceptions import ClientResponseError

from app.domain.models import TitlePagination
from ..base_provider import BaseProvider, Title
from .parser import MalParser
from app.core import logger


class MalProvider(BaseProvider):
    """
    Provider for MyAnimeList (MAL) API.
    This class is responsible for interacting with the MAL API to fetch data.
    """

    def __init__(self, base_url="https://api.jikan.moe/v4/"):
        """Initialize the MAL provider with the base URL."""
        super().__init__(base_url=base_url)

    async def __aenter__(self) -> "MalProvider":
        """Async context manager entry."""
        return self

    async def get_by_id(self, id: int, proxy: str | None = None) -> Title | int | None:  # type: ignore
        """
        Fetch title data by ID from MyAnimeList.

        Args:
            id (int): The ID of the title to fetch.
            proxy (str | None): Optional proxy URL for the request.

        Returns:
            Title | int | None: Parsed title data if successful, HTTP status code if an error occurs, or None if no data is found.

        """
        try:
            data = await self.get(url=f"manga/{id}", proxy=proxy)

            if not data:
                return

            return MalParser.parse(data["data"])
        except ClientResponseError as e:
            return e.status
        except Exception as e:
            logger.error(f"Error fetching data from MAL for ID {id}: {e}")
            return

    async def get_page(
        self,
        page: int,
        limit: int = 25,
        proxy: str | None = None,
    ) -> TitlePagination:
        """
        Fetch a page of titles from MyAnimeList.

        Args:
            page (int): The page number to fetch.
            limit (int): The number of titles per page (default is 25).

        Returns:
            TitlePagination: A pagination object containing the list of titles and pagination info.
        """
        try:
            data = await self.get(
                url="manga",
                proxy=proxy,
                params={
                    "page": page,
                    "limit": limit,
                },
            )

            if not data or "data" not in data:
                return TitlePagination()

            return MalParser.parse_page(data)
        except ClientResponseError as e:
            logger.error(f"Error fetching page from MAL: {e}")
            return TitlePagination()
