from aiohttp.client_exceptions import ClientResponseError
from aiohttp import ClientTimeout
from abc import ABC, abstractmethod

from app.infrastructure.db.models import Title
from app.domain.models import TitlePagination
from app.utils import AsyncHttpClient


class BaseProvider(ABC, AsyncHttpClient):
    """
    Base class for all providers.
    Providers should inherit from this class and implement the required methods.
    """

    def __init__(
        self,
        base_url: str | None = None,
        timeout: float = 15.0,
    ):
        """
        Initialize the provider with any necessary arguments.

        Args:
            base_url: Base URL for the API
            timeout: Timeout for requests in seconds
        """
        super().__init__(
            base_url=base_url,
            timeout=timeout,
            disable_ssl=True,
        )

    @abstractmethod
    async def get_by_id(self, id: int | str, proxy: str | None = None) -> Title | None:
        """
        Method for retrieving title data from a specified provider by id.
        """
        raise NotImplementedError("This method should be implemented by subclasses.")

    @abstractmethod
    async def get_page(
        self,
        page: int,
        limit: int = 25,
        proxy: str | None = None,
    ) -> TitlePagination:
        """
        Method for retrieving a page of titles from a specified provider.

        Args:
            page (int): The page number to fetch.
            limit (int): The number of titles per page (default is 25).
            proxy (str | None): Optional proxy URL for the request.

        Returns:
            TitlePagination: A pagination object containing the list of titles and pagination info.
        """
        raise NotImplementedError("This method should be implemented by subclasses.")