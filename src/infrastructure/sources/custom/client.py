from ..base_provider import *
from .parser import CustomParser


class CustomClient(BaseProvider):
    """
    Template implementation of a data provider.
    Customize this class to integrate with your API source.
    """

    BASE_URL = "https://your-api.com/api/"
    REQUESTS_PER_SECOND = 3.0

    async def get_by_id(self, external_id: str) -> SourceTitleData | None:
        """
        Fetch title data by external ID.

        Returns None if the title is not found.
        Exception handling is managed by the base class.
        """
        async with self.get(f"manga/{external_id}") as response:
            data = await response.json()
            if "data" not in data:
                return None

            return CustomParser.parse_title(data["data"])

    async def get_page(self, page: int = 1, limit: int = 25) -> list[SourceTitleData]:
        """
        Fetch a page of titles from the API catalog.

        Returns an empty list if no data is available.
        Exception handling is managed by the base class.
        """
        if page < 1 or not (1 <= limit <= 25):
            raise ValueError("Page must be >= 1 and limit must be between 1 and 25.")

        async with self.get("manga", params={"page": page, "limit": limit}) as response:
            data = await response.json()

            if not data or "data" not in data:
                return []

            return CustomParser.parse_page(data)

    async def get_source_detail(self) -> SourceDetail:
        """
        Fetch metadata about the source.

        Returns source details including total pages and items per page.

        Note: Different sources compute total_pages differently:
        - Some APIs provide this value directly in response metadata
        - Some sources have hardcoded limits (e.g., Remanga caps at 999 pages)
        - Some require binary search to determine the actual limit
        """
        return SourceDetail(
            source=Source.CUSTOM,
            total_pages=1000,
            items_per_page=30,
        )
