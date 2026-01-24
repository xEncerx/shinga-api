from ..base_provider import *
from .parser import RemangaParser


class RemangaClient(BaseProvider):
    BASE_URL = "https://api.remanga.org/api/"
    REQUESTS_PER_SECOND = 5.0

    async def get_by_id(self, external_id: str) -> SourceTitleData | None:
        async with self.get(f"v2/titles/{external_id}/") as response:
            data = await response.json()
            if not data:
                return None

            return RemangaParser.parse_title(data)

    async def get_page(
        self,
        page: int = 1,
        limit: int = 30,
    ) -> list[SourceTitleData]:
        if not (1 <= page <= 1998):
            raise ValueError(f"Page must be between 1 and 1998.")
        if not (1 <= limit <= 30):
            raise ValueError("Limit must be between 1 and 30.")

        # Remanga has a limitation on the page parameter (maximum 999 pages)
        # Therefore, for pages > 1000, we simply change the sorting order to reverse
        # Thus, we can get all 1998 pages
        api_page, ordering = (page, "id") if page < 1000 else (1999 - page, "-id")

        async with self.get(
            "v2/search/catalog/",
            params={
                "page": api_page,
                "count": limit,
                "ordering": ordering,
            },
        ) as response:
            data = await response.json()

            if not data or not data["results"]:
                return []

            return RemangaParser.parse_page(data)

    async def get_source_detail(self) -> SourceDetail:
        return SourceDetail(
            source=Source.REMANGA,
            total_pages=1998,
            items_per_page=30,
        )
