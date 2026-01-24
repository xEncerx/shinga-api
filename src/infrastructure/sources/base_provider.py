from abc import ABC, abstractmethod

from aiolimiter import AsyncLimiter

from src.domain.models.titles import SourceDetail, SourceTitleData
from src.domain.models.source import Source
from src.infrastructure.network import AsyncHttpClient


class BaseProvider(ABC, AsyncHttpClient):
    """
    Interface for title data providers.
    """

    # Base URL for the provider's API.
    BASE_URL: str | None = None
    # Maximum number of requests per second allowed for this provider.
    REQUESTS_PER_SECOND: float | None = None

    def __init__(
        self,
        timeout: float = 10,
        disable_ssl: bool = False,
        proxy: str | None = None,
    ) -> None:
        """
        Initialize the base provider.

        - Automatically sets up rate limiting based on REQUESTS_PER_SECOND.

        Args:
            timeout (float): Timeout for HTTP requests.
            disable_ssl (bool): Whether to disable SSL verification.
            proxy (str | None): Proxy URL if needed.
        """

        limiter: AsyncLimiter | None = None
        if self.REQUESTS_PER_SECOND:
            limiter = AsyncLimiter(self.REQUESTS_PER_SECOND, 1)

        super().__init__(self.BASE_URL, timeout, disable_ssl, proxy, limiter)

    @abstractmethod
    async def get_by_id(self, external_id: str) -> SourceTitleData | None:
        """
        Method for retrieving title data from a specified provider by id.
        """
        raise NotImplementedError("This method should be implemented by subclasses.")

    @abstractmethod
    async def get_page(
        self,
        page: int = 1,
        limit: int = 25,
    ) -> list[SourceTitleData]:
        """
        Method for retrieving a page of titles from a specified provider.
        """
        raise NotImplementedError("This method should be implemented by subclasses.")

    @abstractmethod
    async def get_source_detail(self) -> SourceDetail:
        """Method for retrieving source detail information."""
        raise NotImplementedError("This method should be implemented by subclasses.")
