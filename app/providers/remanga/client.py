from .parser import RemangaParser
from ..base_provider import *
from app.core import logger

from datetime import datetime
from typing import Literal


class RemangaProvider(BaseProvider):
    """
    Provider for Remanga API.
    This class is responsible for interacting with the Remanga API to fetch data.
    """

    MAX_PAGES = 999  # Remanga API limitation

    def __init__(self, base_url="https://api.remanga.org/api/"):
        """Initialize the Remanga provider with the base URL."""
        super().__init__(base_url=base_url)

    @handle_provider_errors("REMANGA")
    async def get_by_id(
        self, id: int | str, proxy: str | None = None
    ) -> TitleData | None:
        """
        Fetch title data by slug from Remanga.

        Args:
            id (str): The slug of the title to fetch.
            proxy (str | None): Optional proxy URL for the request.

        Returns:
            TitleData | None: Parsed title data if successful or None if no data is found or an error occurs.
        """
        async with self.get(f"v2/titles/{id}/", proxy=proxy) as response:
            response.raise_for_status()
            data = await response.json()

        if not data:
            raise ProviderDataError(f"Remanga returned empty data for slug {id}")

        return RemangaParser.parse(data)

    @handle_provider_errors("REMANGA")
    async def get_page(
        self,
        page: int,
        limit: int = 30,
        proxy: str | None = None,
        ordering: Literal["id", "-id"] = "-id",  # type: ignore
        **unused,
    ) -> TitlePagination[TitleData]:
        """
        Fetch a page of titles from Remanga.
        Args:
            page (int): The page number to fetch.
            limit (int): The number of titles per page (default is 30/30 of max pages).
            proxy (str | None): Optional proxy URL for the request.
            ordering (str): The ordering of titles.
            **unused: Additional provider-specific parameters.

        Returns:
            TitlePagination[TitleData]: A pagination object containing the list of titles and pagination info.
        """
        if not (1 <= page < self.MAX_PAGES):
            raise ValueError(f"Page must be between 1 and {self.MAX_PAGES}.")
        if not (1 <= limit <= 30):
            raise ValueError("Limit must be between 1 and 30.")

        async with self.get(
            f"v2/search/catalog/?page={page}&count={limit}&ordering={ordering}",
            proxy=proxy,
        ) as response:
            response.raise_for_status()
            data = await response.json()

        if not data or not data["results"]:
            raise ProviderDataError(
                f"Remanga returned empty/invalid data for page {page}"
            )

        return RemangaParser.parse_page(data)

    async def get_total_pages(self, limit: int = 30, proxy: str | None = None) -> int:
        """
        Get total pages from Remanga.

        Remanga has API limitation: max 999 pages.
        We use bidirectional scraping to get more coverage.
        """
        return self.MAX_PAGES

    async def get_scraping_config(self, proxy: str | None = None) -> dict:
        """
        Get Remanga-specific scraping configuration.

        Uses bidirectional strategy:
        - Even days: -id (newest to oldest)
        - Odd days: id (oldest to newest)

        This ensures we get full coverage despite 999 page limit.
        """
        total_pages = await self.get_total_pages(proxy=proxy)

        # Determine direction based on current day
        current_day = datetime.now().day
        is_even_day = current_day % 2 == 0
        ordering = "-id" if is_even_day else "id"

        config = {
            "total_pages": total_pages,
            "ordering": ordering,
        }

        return config
