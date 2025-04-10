from httpx import AsyncClient

from ..serializer import remanga_serializer
from ..base_api import BaseMangaAPI

from app.models import MangaResponse
from app.utils import tag_remover


class RemangaAPI(BaseMangaAPI):
    _API_URL = "https://api.remanga.org/api"

    def __init__(self, client: AsyncClient | None = None):
        super().__init__(client)

    async def search(
        self,
        query: str,
        limit: int = 1,
        by_slug: bool = False,
    ) -> MangaResponse:
        url = (
            f"{self._API_URL}/titles/{query}"
            if by_slug
            else f"{self._API_URL}/search/?query={query}/&count={limit}"
        )

        response = await self._handle_request(
            self._client.get,
            url,
            follow_redirects=True,
        )
        response = remanga_serializer(response)

        return MangaResponse(content=response)

    async def suggest(self, query: str) -> MangaResponse:
        response = await self._handle_request(
            self._client.get,
            f"{self._API_URL}/v2/search/?count=10&field=titles&page=1&query={query}",
            follow_redirects=True,
        )

        suggestions = [tag_remover(data["main_name"]) for data in response["results"]]

        return MangaResponse(content=suggestions)
