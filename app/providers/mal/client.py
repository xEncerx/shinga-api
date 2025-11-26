from ..base_provider import *
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

    @handle_provider_errors("MAL")
    async def get_by_id(
        self, id: int | str, proxy: str | None = None
    ) -> TitleData | None:
        """
        Fetch title data by ID from MyAnimeList.

        Args:
            id (int): The ID of the title to fetch.
            proxy (str | None): Optional proxy URL for the request.

        Returns:
            TitleData | None: Parsed title data if successful or None if no data is found or an error occurs.
        """
        async with self.get(f"manga/{id}", proxy=proxy) as response:
            response.raise_for_status()
            data = await response.json()

        if not data:
            raise ProviderDataError(f"MAL returned empty data for ID {id}")

        return MalParser.parse(data["data"])

    @handle_provider_errors("MAL")
    async def get_page(
        self,
        page: int,
        limit: int = 25,
        proxy: str | None = None,
        **unused,
    ) -> TitlePagination[TitleData]:
        """
        Fetch a page of titles from MyAnimeList.

        Args:
            page (int): The page number to fetch.
            limit (int): The number of titles per page (default is 25/25 of max pages).
            proxy (str | None): Optional proxy URL for the request.
            **unused: Additional provider-specific parameters.

        Returns:
            TitlePagination[TitleData]: A pagination object containing the list of titles and pagination info.
        """
        if page < 1 or not (1 <= limit <= 25):
            raise ValueError("Page must be >= 1 and limit must be between 1 and 25.")

        async with self.get(
            f"manga?page={page}&limit={limit}",
            proxy=proxy,
        ) as response:
            response.raise_for_status()
            data = await response.json()

        if not data or "data" not in data:
            raise ProviderDataError(f"MAL returned empty/invalid data for page {page}")

        return MalParser.parse_page(data)

    async def get_total_pages(self, limit: int = 25, proxy: str | None = None) -> int:
        """
        Get total number of pages from MAL.

        Strategy: Fetch page 1 and check pagination.last_visible_page
        """
        try:
            # Fetch first page to get pagination info
            pagination = await self.get_page(page=1, limit=limit, proxy=proxy)

            if not pagination or not pagination.pagination:
                logger.warning(
                    "MAL: Could not get pagination info, defaulting to 100 pages"
                )
                return 100  # Fallback default

            # MAL returns last_visible_page in pagination
            total_pages = pagination.pagination.last_visible_page or 100

            logger.info(f"MAL: Total available pages: {total_pages}")
            return total_pages

        except Exception as e:
            logger.error(f"MAL: Error getting total pages: {e}, defaulting to 100")
            return 100  # Fallback on error
