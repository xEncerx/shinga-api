from httpx import AsyncClient

from ..base_api import BaseMangaAPI

from app.models import MangaResponse
from app.utils import tag_remover


class MangaPoisk(BaseMangaAPI):
    _API_URL = "https://mangapoisk.live"

    def __init__(self, client: AsyncClient | None = None):
        super().__init__(client)

    async def suggest(self, query: str) -> MangaResponse:
        response = await self._handle_request(
            self._client.get,
            f"{self._API_URL}/search?q={query}",
            follow_redirects=True,
            headers={"Accept": "application/json"},
        )
        suggestions = [tag_remover(data["label"]) for data in response["results"]]
        return MangaResponse(content=suggestions)

    async def search(
        self,
        query: str,
        limit: int = 1,
        by_slug: bool = False,
    ) -> MangaResponse:
        raise NotImplementedError("MangaPoisk search method is not implemented yet.")
