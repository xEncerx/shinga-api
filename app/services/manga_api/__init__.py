from fastapi_cache.coder import PickleCoder
from fastapi_cache.decorator import cache
from fastapi import HTTPException
import asyncio

from app.models import MangaResponse
from app.core import MC

from .base_api import BaseMangaAPI
from .client import *


class MangaAPI(BaseMangaAPI):
    def __init__(self):
        super().__init__()

        self.remanga = RemangaAPI()
        self.shikimori = ShikimoriAPI()
        self.manga_poisk = MangaPoisk()

    @cache(expire=60 * 30, coder=PickleCoder)
    async def search(
        self,
        query: str,
        limit: int = 10,
        by_slug: bool = False,
    ) -> MangaResponse:
        """
        Search for manga using all available APIs.
        Args:
                query (str): The search query string.
                limit (int, optional): Maximum number of results to return per source. Defaults to 10.
                by_slug (bool, optional): If True, searches by manga slug instead of title. Defaults to False.
        Returns:
                MangaResponse: A response object containing combined manga content from all sources.
        Note:
                Results are cached for 30 minutes using pickle serialization.
        Example:
                ```
                result = await manga_api.search("One Piece", limit=5)
                ```
        """
        remanga_task = self.remanga.search(
            query=query,
            limit=limit,
            by_slug=by_slug,
        )
        shikimori_task = self.shikimori.search(
            query=query,
            limit=limit,
            by_slug=by_slug,
        )

        remanga_response, shikimori_response = await asyncio.gather(
            remanga_task,
            shikimori_task,
        )

        content = remanga_response.content + shikimori_response.content

        return MangaResponse(content=content)

    @cache(expire=60 * 30, coder=PickleCoder)
    async def search_by_source(
        self,
        query: str,
        source: str,
        limit: int = 1,
        bySlug: bool = True,
    ) -> MangaResponse:
        """
        Search manga from a specific source based on a query.
        Args:
                query (str): The search query string to look for.
                source (str): The source to search in. Must be one of the sources defined in MC.Sources.
                limit (int, optional): Maximum number of results to return. Defaults to 1.
                bySlug (bool, optional): Whether to search by slug/URL-friendly format. Defaults to True.
        Returns:
                MangaResponse: The response containing manga search results from the specified source.
        Raises:
                HTTPException: If the provided source is not supported for searching.
        """

        match source:
            case MC.Sources.REMANGA:
                response = await self.remanga.search(
                    query=query, limit=limit, by_slug=bySlug
                )
            case MC.Sources.SHIKIMORI:
                response = await self.shikimori.search(
                    query=query, limit=limit, by_slug=bySlug
                )
            case MC.Sources.MANGA_POISK:
                response = await self.manga_poisk.search(
                    query=query, limit=limit, by_slug=bySlug
                )
            case _:
                raise HTTPException(
                    status_code=400, detail=f"Unsupported source for this action"
                )

        return response

    async def suggest(self, query: str, source: MC.Sources) -> MangaResponse:
        """
        Suggests manga titles based on a search query from a specified source.
        Args:
                query (str): The search query to find manga titles.
                source (MC.Sources): The source to search for manga. Supported sources are REMANGA and MANGA_POISK.
        Returns:
                MangaResponse: An object containing the suggested manga titles.
        Raises:
                HTTPException: If an unsupported source is provided, raises a 400 Bad Request error.
        """

        match source:
            case MC.Sources.REMANGA:
                response = await self.remanga.suggest(query)
            case MC.Sources.MANGA_POISK:
                response = await self.manga_poisk.suggest(query)
            case _:
                raise HTTPException(
                    status_code=400, detail=f"Unsupported source for this action"
                )

        return response


manga_api = MangaAPI()
