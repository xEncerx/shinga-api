from httpx import AsyncClient

from ..serializer import shikimori_serializer
from ..base_api import BaseMangaAPI

from app.models import MangaResponse


class ShikimoriAPI(BaseMangaAPI):
    _API_URL = "https://shikimori.one/api/graphql"
    _QUERY = """
	{
	  mangas(%s, limit: %s) {
		id
		name
		russian
		english
		japanese
		synonyms
		score
		status
		chapters
		airedOn { year }

		poster { originalUrl }

		genres { id name russian kind }
		statusesStats { count }
		description
	  }
	}
	"""

    def __init__(self, client: AsyncClient | None = None):
        super().__init__(client)

    async def search(
        self,
        query: str,
        limit: int = 1,
        by_slug: bool = False,
    ) -> MangaResponse:
        search_by = f'ids: "{query}"' if by_slug else f'search: "{query}"'

        response = await self._handle_request(
            self._client.post,
            self._API_URL,
            follow_redirects=True,
            json={"query": self._QUERY % (search_by, limit)},
        )
        response = shikimori_serializer(response)

        return MangaResponse(content=response)
