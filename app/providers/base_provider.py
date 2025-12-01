from aiohttp.client_exceptions import ClientResponseError, ClientConnectionError

from asyncio import TimeoutError as AsyncioTimeoutError
from typing import TypeVar, Callable
from abc import ABC, abstractmethod
from functools import wraps

from app.domain.models import TitlePagination, TitleData
from app.infrastructure.http import AsyncHttpClient
from app.domain.models.exceptions import *
from app.core import logger


T = TypeVar("T")


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
    async def get_by_id(
        self, id: int | str, proxy: str | None = None
    ) -> TitleData | None:
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
        **kwargs,
    ) -> TitlePagination[TitleData]:
        """
        Method for retrieving a page of titles from a specified provider.

        Args:
            page (int): The page number to fetch.
            limit (int): The number of titles per page (default is 25).
            proxy (str | None): Optional proxy URL for the request.
            **kwargs: Additional provider-specific parameters.

        Returns:
            TitlePagination[TitleData]: A pagination object containing the list of titles and pagination info.
        """
        raise NotImplementedError("This method should be implemented by subclasses.")

    @abstractmethod
    async def get_total_pages(self, limit: int = 25, proxy: str | None = None) -> int:
        """
        Get total number of available pages from the provider.

        This method should be implemented to determine how many pages
        are available for scraping. Each provider has its own logic:
        - MAL/Shikimori: Check pagination info from first page
        - Remanga: Return hardcoded limit (1000)
        - Other: Custom logic based on API capabilities

        Args:
            limit: Items per page (affects total page count)
            proxy: Optional proxy URL

        Returns:
            Total number of pages available for scraping
        """
        raise NotImplementedError("This method should be implemented by subclasses.")

    async def get_scraping_config(self, proxy: str | None = None) -> dict:
        """
        Get scraping configuration for this provider.

        Returns:
            Dictionary with scraping configuration:
            - total_pages: Total number of pages available
            - other provider-specific settings
        """
        total_pages = await self.get_total_pages(proxy=proxy)

        return {"total_pages": total_pages}


def handle_provider_errors(provider_name: str):
    """Decorator to handle common provider errors."""

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            try:
                return await func(*args, **kwargs)  # type: ignore

            except ClientResponseError as e:
                # HTTP response errors (429, 4xx, 5xx, etc.)
                context = f"{kwargs.get('page', kwargs.get('id', 'unknown'))}"

                if e.status == 429:
                    retry_after = int(e.headers.get("Retry-After", 60))
                    logger.warning(
                        f"{provider_name} rate limit hit on {context}, "
                        f"retry after {retry_after}s"
                    )
                    raise RateLimitError(
                        f"{provider_name} rate limit exceeded for {context}",
                        retry_after=retry_after,
                    ) from e

                elif 500 <= e.status < 600:
                    logger.error(
                        f"{provider_name} server error {e.status} on {context}"
                    )
                    raise ProviderUnavailableError(
                        f"{provider_name} server error {e.status} for {context}"
                    ) from e

                else:
                    logger.error(f"{provider_name} error {e.status} on {context}")
                    raise ProviderException(
                        f"{provider_name} error {e.status} for {context}"
                    ) from e

            except (
                RateLimitError,
                ProviderUnavailableError,
                ProviderDataError,
                ProviderException,
            ):
                # Re-raise domain exceptions as-is
                raise

            except (
                TimeoutError,
                AsyncioTimeoutError,
                ClientConnectionError,
                ConnectionError,
            ) as e:
                # Network/timeout errors - forward for retry
                logger.warning(
                    f"{provider_name} network/timeout error: {type(e).__name__}"
                )
                raise ProviderUnavailableError(
                    f"{provider_name} connection error: {type(e).__name__}"
                ) from e

            except Exception as e:
                logger.error(f"{provider_name} unexpected error: {e}", exc_info=True)
                raise ProviderException(
                    f"Unexpected error in {provider_name}: {str(e)}"
                ) from e

        return wrapper  # type: ignore

    return decorator
