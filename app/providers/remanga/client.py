from aiohttp import ClientTimeout

from ..base_provider import *
from .parser import RemangaParser
from app.core import logger


class RemangaProvider(BaseProvider):
    """
    Provider for Remanga API.
    This class is responsible for interacting with the Remanga API to fetch data.
    """
    def __init__(self, base_url="https://api.remanga.org/api/"):
        """Initialize the Remanga provider with the base URL."""
        super().__init__(base_url=base_url)

    async def __aenter__(self) -> "RemangaProvider":
        """Async context manager entry."""
        return self

    async def get_by_id(self, id: int | str, proxy: str | None = None) -> Title | None:
        """
        Fetch title data by slug from Remanga.

        Args:
            id (str): The slug of the title to fetch.
            proxy (str | None): Optional proxy URL for the request.

        Returns:
            Title | None: Parsed title data if successful or None if no data is found or an error occurs.

        """
        try:
            data = await self.get(url=f"v2/titles/{id}/", proxy=proxy)

            if not data:
                return

            return RemangaParser.parse(data)
        except Exception as e:
            logger.error(f"Error fetching data from Remanga for slug {id}: {e}")
            return

    async def get_page(
        self,
        page: int,
        limit: int = 50,
        proxy: str | None = None,
    ) -> TitlePagination:
        """
        Fetch a page of titles from Remanga.
        ! Remanga has't yet fixed the bug and u can get an unlimited titles per page.

        Args:
            page (int): The page number to fetch.
            limit (int): The number of titles per page (default is 50/∞ of max pages).
            proxy (str | None): Optional proxy URL for the request.

        Returns:
            TitlePagination: A pagination object containing the list of titles and pagination info.
        """
        if page < 1:
            raise ValueError("Page must be >= 1")

        try:
            data = await self.get(
                url=f"v2/search/catalog/?page={page}&count={limit}&ordering=-id",
                proxy=proxy,
                timeout=ClientTimeout(total=100)
            )

            if not data or not data["results"]:
                return TitlePagination()

            return RemangaParser.parse_page(data)
        except Exception as e:
            logger.error(f"Error fetching page from Remanga: {e}")
            return TitlePagination()
