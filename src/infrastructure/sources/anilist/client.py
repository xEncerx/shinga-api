from ..base_provider import *
from .parser import AniListParser

import asyncio


class AniListClient(BaseProvider):
    _CATALOG_QUERY = """
    query {
        results: Page(page: %s, perPage: %s) {
            pageInfo {
                total
                currentPage
                lastPage
                hasNextPage
                perPage
            }
            media(
                sort: POPULARITY_DESC
                type: MANGA
            ) {
                ...media
            }
        }
    }
    fragment media on Media {
        id
        idMal
        title { userPreferred english }
        coverImage { extraLarge large medium }
        startDate { year month day }
        endDate { year month day }
        description
        type
        synonyms
        status(version: 2)
        chapters
        volumes
        genres
        favourites
        popularity
        siteUrl
        tags {
            name
        }
        stats {
            scoreDistribution {
                score
                amount
            }
        }
        staff(page: 1, perPage: 5, sort: [RELEVANCE, FAVOURITES_DESC]) {
            edges {
                node {
                    name {
                        full
                    }
                }
            }
        }
    }
    """
    _TITLE_QUERY = """
    query {
        Media(id: %s) {
            id
            idMal
            title { userPreferred english }
            coverImage { extraLarge large medium }
            startDate { year month day }
            endDate { year month day }
            description
            type
            synonyms
            status(version: 2)
            chapters
            volumes
            genres
            favourites
            popularity
            siteUrl
            tags {
                name
            }
            stats {
                scoreDistribution {
                    score
                    amount
                }
            }
            staff(page: 1, perPage: 5, sort: [RELEVANCE, FAVOURITES_DESC]) {
                edges {
                    node {
                        name {
                            full
                        }
                    }
                }
            }
        }
    }
    """

    BASE_URL = "https://graphql.anilist.co"

    RATE_LIMIT_REQUESTS = 1
    RATE_LIMIT_PERIOD = 4

    async def get_by_id(self, external_id: str) -> SourceTitleData | None:
        async with self.post(
            "", json={"query": self._TITLE_QUERY % external_id}
        ) as response:
            data = await response.json()

            if data["data"]["Media"] is None:
                return None

            return AniListParser.parse_title(data["data"]["Media"])

    async def get_page(self, page: int = 1, limit: int = 50) -> list[SourceTitleData]:
        if page < 1 or not (1 <= limit <= 50):
            raise ValueError("Page must be >= 1 and limit must be between 1 and 50.")

        async with self.post(
            "", json={"query": self._CATALOG_QUERY % (page, limit)}
        ) as response:
            data = await response.json()

            if not data["data"]["results"]["media"]:
                return []

            return AniListParser.parse_page(data)

    async def get_source_detail(self) -> SourceDetail:
        return SourceDetail(
            source=Source.ANILIST,
            total_pages=await self._get_total_pages(),
            items_per_page=50,
        )

    # === Utils method for getting total pages by binary search ===
    async def _get_total_pages(self) -> int:
        low = 1
        high = 3000  # Arbitrary high value

        while low < high:
            mid = (low + high + 1) // 2
            if await self._has_data(mid):
                low = mid
            else:
                high = mid - 1
            await asyncio.sleep(3)  # Respect rate limit

        return low

    _BINARY_SEARCH_QUERY = """
    query {
        results: Page(page: %s, perPage: 50) {
            pageInfo {
                hasNextPage
            }
            media(
                type: MANGA
            ) {
                ...media
            }
        }
    }
    fragment media on Media {
        id
    }
    """

    async def _has_data(self, page: int) -> bool:
        async with self.post(
            "", json={"query": self._BINARY_SEARCH_QUERY % page}
        ) as response:
            data = await response.json()
            hasNextPage = data["data"]["results"]["pageInfo"]["hasNextPage"]

        return hasNextPage
