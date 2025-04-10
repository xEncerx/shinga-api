from httpx import AsyncClient, HTTPStatusError, Response, AsyncHTTPTransport, Limits
from abc import ABC, abstractmethod
from typing import Callable, Any

from app.models import MangaResponse
from app.utils import logger


class BaseMangaAPI(ABC):
    """Base class for Manga API."""

    _API_URL: str
    _client: AsyncClient

    def __init__(self, client: AsyncClient | None = None):
        if not client:
            transport = AsyncHTTPTransport(retries=3)
            limits = Limits(max_connections=100, max_keepalive_connections=20)
            client = AsyncClient(transport=transport, limits=limits, timeout=10.0)

        self._client = client

    async def _handle_request(
        self,
        request_func: Callable,
        *args,
        **kwargs,
    ) -> list[str, Any]:
        try:
            response: Response = await request_func(*args, **kwargs)
            response.raise_for_status()

            return response.json()

        except HTTPStatusError as e:
            logger.error(f"{self.__class__.__name__}: {e}")
            return MangaResponse(message="Could not find any data", content=[])

        except Exception as e:
            logger.exception(f"Unexpected error in {self.__class__.__name__}")
            return MangaResponse(message=str(e), content=[])

    @abstractmethod
    async def search(
        self,
        query: str,
        limit: int = 1,
        by_slug: bool = False,
    ) -> MangaResponse:
        """Abstract manga search method."""
        pass
