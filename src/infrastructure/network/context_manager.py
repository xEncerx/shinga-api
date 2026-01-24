from aiohttp import (
    ClientConnectorError,
    ClientResponseError,
    ServerTimeoutError,
    ClientResponse,
    ClientError,
)
from aiolimiter import AsyncLimiter

from asyncio import TimeoutError
from typing import Any, Coroutine, Generator, Optional, Type
from types import TracebackType

from .exceptions import (
    HttpConnectionError,
    HttpTimeoutError,
    HttpClientError,
    HttpServerError,
    HttpError,
)

__all__ = ["RequestContextManager"]


class RequestContextManager:
    """
    Context manager wrapper that handles aiohttp exceptions and converts them
    to application-specific exceptions.
    """

    __slots__ = ("_coro", "_resp", "_url", "_limiter")

    def __init__(
        self,
        coro: Coroutine[Any, Any, ClientResponse],
        url: str,
        limiter: AsyncLimiter | None = None,
    ) -> None:
        """
        Initialize the RequestContextManager.

        Args:
            coro: The coroutine that performs the HTTP request.
            url: The URL being requested (for error messages).
            limiter: An optional AsyncLimiter to limit the rate of requests.
        """

        self._coro = coro
        self._resp: Optional[ClientResponse] = None
        self._url = url
        self._limiter = limiter

    def __await__(self) -> Generator[Any, None, ClientResponse]:
        return self._coro.__await__()

    def __iter__(self) -> Generator[Any, None, ClientResponse]:
        return self.__await__()

    async def __aenter__(self) -> ClientResponse:
        if self._limiter is not None:
            await self._limiter.acquire()

        try:
            self._resp = await self._coro
            await self._resp.__aenter__()

            # Check HTTP status
            try:
                self._resp.raise_for_status()
            except ClientResponseError as e:
                if 400 <= e.status < 500:
                    raise HttpClientError(
                        f"Client error {e.status}: {e.message}",
                        status_code=e.status,
                    ) from e
                elif 500 <= e.status < 600:
                    raise HttpServerError(
                        f"Server error {e.status}: {e.message}",
                        status_code=e.status,
                    ) from e
                else:
                    raise HttpError(
                        f"HTTP error {e.status}: {e.message}",
                        status_code=e.status,
                    ) from e

            return self._resp

        except (ServerTimeoutError, TimeoutError) as e:
            raise HttpTimeoutError(f"Request to {self._url} timed out") from e
        except ClientConnectorError as e:
            raise HttpConnectionError(
                f"Failed to connect to {self._url}: {str(e)}"
            ) from e
        except ClientError as e:
            raise HttpError(f"HTTP request failed: {str(e)}") from e

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> None:
        if self._resp is not None:
            await self._resp.__aexit__(exc_type, exc_value, traceback)
