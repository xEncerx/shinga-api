from .parser import ShikimoriParser
from ..base_provider import *
from app.core import logger

import asyncio


class ShikimoriProvider(BaseProvider):
    _QUERY = """
	{
	  mangas(%s) {
            id
            malId
            russian
            english
            name
            licenseNameRu
            japanese
            synonyms
            kind
            score
            scoresStats { count }
            status
            statusesStats  { count }
            volumes
            chapters
            airedOn { year month day date }
            releasedOn { year month day date }
            poster { id originalUrl mainUrl }
            genres { id name russian }

            personRoles {
                id
                rolesRu
                rolesEn
                person { id name poster { id } }
            }

            description
        }
	}
	"""

    def __init__(self, base_url="https://shikimori.one/api/graphql/"):
        super().__init__(base_url=base_url)

    @handle_provider_errors("SHIKIMORI")
    async def get_by_id(
        self, id: int | str, proxy: str | None = None
    ) -> TitleData | None:
        """
        Fetch title data by id from Shikimori.

        Args:
            id (str): The id of the title to fetch.
            proxy (str | None): Optional proxy URL for the request.

        Returns:
            TitleData | None: Parsed title data if successful or None if no data is found or an error occurs.
        """
        arguments = f'ids: "{id}"'

        async with self.post(
            "", proxy=proxy, json={"query": self._QUERY % arguments}
        ) as response:
            response.raise_for_status()
            data = await response.json()

        if not data or not data["data"]["mangas"]:
            raise ProviderDataError(f"Shikimori returned empty data for id {id}")

        return ShikimoriParser.parse(data["data"]["mangas"][0])

    @handle_provider_errors("SHIKIMORI")
    async def get_page(
        self,
        page: int,
        limit: int = 50,
        proxy: str | None = None,
        **unused,
    ) -> TitlePagination[TitleData]:
        """
        Fetch a page of titles from Shikimori.

        Args:
            page (int): The page number to fetch.
            limit (int): The number of titles per page (default is 50/50 of max pages).
            proxy (str | None): Optional proxy URL for the request.
            **unused: Additional provider-specific parameters.

        Returns:
            TitlePagination[TitleData]: A pagination object containing the list of titles and pagination info.
        """
        if page < 1 or not (1 <= limit <= 50):
            raise ValueError("Page must be >= 1 and limit must be between 1 and 50.")

        arguments = f"page: {page}, limit: {limit}"

        async with self.post(
            "",
            proxy=proxy,
            json={"query": self._QUERY % arguments},
        ) as response:
            response.raise_for_status()
            data = await response.json()

        if not data or not data["data"]["mangas"]:
            raise ProviderDataError(
                f"Shikimori returned empty/invalid data for page {page}"
            )

        return ShikimoriParser.parse_page(data)

    async def get_total_pages(self, limit: int = 50, proxy: str | None = None) -> int:
        """
        Find last non-empty page using binary search.

        Args:
            limit: Items per page (default 50)
            proxy: Proxy URL

        Returns:
            Last page number with data
        """
        logger.info("Shikimori: Starting binary search for last page...")

        # Initial bounds
        left = 1
        right = 2000  # Upper bound estimate
        last_page_with_data = 1

        # Binary search
        while left <= right:
            mid = (left + right) // 2

            logger.debug(f"Shikimori: Checking page {mid} (range: {left}-{right})")

            has_data = await self._is_page_has_data(mid, limit, proxy)

            if has_data:
                # Page has data - search higher
                last_page_with_data = mid
                left = mid + 1
                logger.debug(f"  → Page {mid} has data, searching higher")
            else:
                # Page is empty - search lower
                right = mid - 1
                logger.debug(f"  → Page {mid} is empty, searching lower")

            await asyncio.sleep(0.3)

        logger.info(f"Shikimori: Last page found: {last_page_with_data}")
        return last_page_with_data

    async def _is_page_has_data(
        self,
        page: int,
        limit: int = 50,
        proxy: str | None = None,
    ) -> bool:
        """
        Quick check if page has data.

        Returns:
            True if page has data, False if empty
        """
        try:
            arguments = f"page: {page}, limit: {limit}"
            async with self.post(
                "", proxy=proxy, json={"query": self._QUERY % arguments}
            ) as response:
                response.raise_for_status()
                data = await response.json()
                data = data.get("data", {}).get("mangas", [])

            # Check if mangas array is not empty
            return data is not None and len(data) > 0

        except Exception as e:
            logger.warning(f"Error checking Shikimori page {page}: {e}")
            return False
