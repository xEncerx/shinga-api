from ..base_provider import *
from .parser import MalParser


class MalClient(BaseProvider):
    BASE_URL = "https://api.jikan.moe/v4/"
    RATE_LIMIT_REQUESTS = 1.2
    RATE_LIMIT_PERIOD = 1

    async def get_by_id(self, external_id: str) -> SourceTitleData | None:
        async with self.get(f"manga/{external_id}") as response:
            data = await response.json()
            if "data" not in data:
                return None

            return MalParser.parse_title(data["data"])

    async def get_page(
        self,
        page: int = 1,
        limit: int = 25,
    ) -> list[SourceTitleData]:
        if page < 1 or not (1 <= limit <= 25):
            raise ValueError("Page must be >= 1 and limit must be between 1 and 25.")

        async with self.get("manga", params={"page": page, "limit": limit}) as response:
            data = await response.json()

            if not data or "data" not in data:
                return []

            return MalParser.parse_page(data)

    async def get_source_detail(self) -> SourceDetail:
        async with self.get("manga/?page=1") as response:
            data = await response.json()
            if "data" not in data:
                raise ValueError("Unable to fetch source detail from MAL API.")

            pagination = data.get("pagination", {})

        return SourceDetail(
            source=Source.MAL,
            total_pages=pagination.get("last_visible_page", 0),
            items_per_page=pagination.get("items", {}).get("per_page", 0),
        )
