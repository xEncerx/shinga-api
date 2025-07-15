from ..base_provider import *
from .parser import ShikiParser
from app.core import logger


class ShikiProvider(BaseProvider):
    _QUERY = """
	{
	  mangas(%s) {
            id
            malId
            russian
            english
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

    async def __aenter__(self) -> "ShikiProvider":
        """Async context manager entry."""
        return self

    async def get_by_id(self, id: int | str, proxy: str | None = None) -> Title | None:
        """
        Fetch title data by id from Shikimori.

        Args:
            id (str): The id of the title to fetch.
            proxy (str | None): Optional proxy URL for the request.

        Returns:
            Title | None: Parsed title data if successful or None if no data is found or an error occurs.

        Raises:
            ClientResponseError: If the request fails with a client error.
        """
        try:
            arguments = f'ids: "{id}"'
            data = await self.post(
                "",
                proxy=proxy,
                json={"query": self._QUERY % arguments}
            )
            if not data or not data["data"]["mangas"]:
                return

            return ShikiParser.parse(data["data"]["mangas"][0])
        except ClientResponseError:
            raise # re-raise to handle it in the worker
        except Exception as e:
            raise e
        
    async def get_page(self, page: int, limit: int = 50, proxy: str | None = None) -> TitlePagination:
        """
        Fetch a page of titles from Shikimori.

        Args:
            page (int): The page number to fetch.
            limit (int): The number of titles per page (default is 50/50 of max pages).
            proxy (str | None): Optional proxy URL for the request.

        Returns:
            TitlePagination: A pagination object containing the list of titles and pagination info.
        """
        if page < 1 or not (1 <= limit <= 50):
            raise ValueError("Page must be >= 1 and limit must be between 1 and 50.")

        try:
            arguments = f'page: {page}, limit: {limit}'
            data = await self.post(
                "",
                proxy=proxy,
                json={"query": self._QUERY % arguments}
            )
            if not data or not data["data"]["mangas"]:
                return TitlePagination()
            
            return ShikiParser.parse_page(data)
        except Exception as e:
            logger.error(f"Error fetching page from Shikimori: {e} - Page: {page}, Limit: {limit}")
            return TitlePagination()