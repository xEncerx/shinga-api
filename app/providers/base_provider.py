from abc import ABC, abstractmethod
from httpx import AsyncClient
from typing import Any

from ..infrastructure.db.models import Title

JsonOrNone = dict[str, Any] | None

class BaseProvider(ABC):
    """
    Base class for all providers.
    Providers should inherit from this class and implement the required methods.
    """

    def __init__(
        self,
        base_url: str | None = None,
        timeout: float = 15.0,
        headers: dict[str, str] | None = None,
    ):
        """
        Initialize the provider with any necessary arguments.

        Args:
            base_url: Base URL for the API
            timeout: Timeout for requests in seconds
            headers: Default headers to include in requests
        """
        self.base_url = base_url
        self.timeout = timeout
        self.default_headers = headers or {}

    @abstractmethod
    async def get_by_id(id: int | str, proxy: str | None) -> Title | None: # type: ignore
        """
        Method for retrieving title data from a specified provider by id.
        """
        pass

    async def request(
        self,
        method: str,
        url: str,
        proxy: str | None = None,
        **kwargs: Any,
    ) -> JsonOrNone:
        """
        Perform an HTTP request.

        Args:
            method: HTTP method (GET, POST, etc.)
            url: URL to request (relative to base_url if base_url is set)
            **kwargs: Additional arguments to pass to httpx (params, json, data, headers, etc.)

        Returns:
            The response from the request
        """
        try:
            async with AsyncClient(
                base_url=self.base_url, # type: ignore
                timeout=self.timeout,
                proxy=proxy,
                headers={
                    **self.default_headers,
                    **kwargs.get("headers", {}),
                },
            ) as client:
                response = await client.request(method, url, **kwargs)
                response.raise_for_status()

                return response.json()
        except Exception as e:
            raise e

    # Get methods for common HTTP verbs
    async def get(self, url: str, **kwargs) -> JsonOrNone:
        return await self.request("GET", url, **kwargs)

    # Post methods for common HTTP verbs
    async def post(self, url: str, **kwargs) -> JsonOrNone:
        return await self.request("POST", url, **kwargs)

    # Put methods for common HTTP verbs
    async def put(self, url: str, **kwargs) -> JsonOrNone:
        return await self.request("PUT", url, **kwargs)

    # Delete methods for common HTTP verbs
    async def delete(self, url: str, **kwargs) -> JsonOrNone:
        return await self.request("DELETE", url, **kwargs)

    # Patch methods for common HTTP verbs
    async def patch(self, url: str, **kwargs) -> JsonOrNone:
        return await self.request("PATCH", url, **kwargs)
