import asyncio

from ..base_provider import *
from .parser import ShikimoriParser


class ShikimoriClient(BaseProvider):
    _QUERY = """
	{
	  mangas(%s) {
            id
            url
            malId
            russian
            english
            name
            licenseNameRu
            synonyms
            kind
            score
            scoresStats { count }
            status
            statusesStats  { count }
            volumes
            chapters
            airedOn { date }
            releasedOn { date }
            poster { originalUrl }
            genres { name kind }
            personRoles { person { name } }
            description
        }
	}
	"""

    BASE_URL = "https://shikimori.one/api/graphql/"
    RATE_LIMIT_REQUESTS = 2
    RATE_LIMIT_PERIOD = 1

    async def get_by_id(self, external_id: str) -> SourceTitleData | None:
        search_param = f'ids: "{external_id}"'

        async with self.post(
            "", json={"query": self._QUERY % search_param}
        ) as response:
            data = await response.json()
            if not data or not data["data"]["mangas"]:
                return None

            return ShikimoriParser.parse_title(data["data"]["mangas"][0])

    async def get_page(
        self,
        page: int = 1,
        limit: int = 50,
    ) -> list[SourceTitleData]:
        if page < 1 or not (1 <= limit <= 50):
            raise ValueError("Page must be >= 1 and limit must be between 1 and 50.")

        search_param = f"page: {page}, limit: {limit}"

        async with self.post(
            "", json={"query": self._QUERY % search_param}
        ) as response:
            data = await response.json()

            if not data or not data["data"]["mangas"]:
                return []

            return ShikimoriParser.parse_page(data)

    async def get_source_detail(self) -> SourceDetail:
        return SourceDetail(
            source=Source.SHIKIMORI,
            total_pages=await self._get_total_pages(),
            items_per_page=50,
        )

    # === Utils method for getting total pages by binary search ===
    async def _get_total_pages(self) -> int:
        low = 1
        high = 2500  # Arbitrary high value

        while low < high:
            mid = (low + high + 1) // 2
            if await self._has_data(mid):
                low = mid
            else:
                high = mid - 1
            await asyncio.sleep(0.3)

        return low

    _BINARY_SEARCH_QUERY = """
    {
        mangas(page: %d, limit: 50) {
            id
        }
    }
    """

    async def _has_data(self, page: int) -> bool:
        async with self.post(
            "", json={"query": self._BINARY_SEARCH_QUERY % page}
        ) as response:
            data = await response.json()
            data = data.get("data", {}).get("mangas", [])

        return data is not None and len(data) > 0
