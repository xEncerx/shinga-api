from aiohttp import (
    ClientSession,
    ClientTimeout,
    TCPConnector,
)
from aiohttp.client import _RequestOptions
from aiohttp.typedefs import StrOrURL
from aiolimiter import AsyncLimiter

from types import TracebackType
import sys

if sys.version_info >= (3, 11):
    from typing import Unpack
else:
    from typing_extensions import Unpack

from .context_manager import RequestContextManager

__all__ = ["AsyncHttpClient"]


class AsyncHttpClient:
    """
    Asynchronous HTTP client wrapper around aiohttp.ClientSession.

    Provides a convenient interface for making HTTP requests with support for
    base URL, custom timeouts, SSL configuration, and proxy settings.

    Should be used as an async context manager to ensure proper session lifecycle management.

    Example:
    ```
    class MyHttpClient(AsyncHttpClient):
        async def fetch_data(self, endpoint: str) -> Any:
            async with self.get(endpoint) as response:
                return await response.json()
    ```
    """

    def __init__(
        self,
        base_url: str | None = None,
        timeout: float = 10.0,
        disable_ssl: bool = False,
        proxy: str | None = None,
        limiter: AsyncLimiter | None = None,
        base_headers: dict[str, str] | None = None,
    ) -> None:
        """
        Initialize the AsyncHttpClient.

        Args:
            base_url: Base URL for all requests. If provided, relative URLs will be appended to it.
            timeout: Request timeout in seconds. Defaults to 10.0 seconds.
            disable_ssl: If True, disables SSL certificate verification. Defaults to False.
            proxy: Proxy server URL to use for requests. Defaults to None.
            limiter: An optional AsyncLimiter to limit the rate of requests. Defaults to None.
            base_headers: Optional headers included in every request.
        """
        self._base_url = base_url
        self._timeout = ClientTimeout(total=timeout)
        self._proxy = proxy
        self._disable_ssl = disable_ssl
        self._session: ClientSession | None = None
        self._limiter = limiter
        self._base_headers = base_headers or {}
        try:
            from fake_useragent import UserAgent

            self._user_agent = UserAgent().random
        except:
            self._user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/"

    @property
    def session(self) -> ClientSession:
        """
        Get the underlying aiohttp ClientSession.

        Returns:
            The active ClientSession instance.

        Raises:
            RuntimeError: If the session is not initialized.
        """
        self._ensure_session()

        return self._session  # type: ignore[return-value]

    # === Request Methods ===
    def request(
        self,
        method: str,
        url: StrOrURL,
        **kwargs: Unpack[_RequestOptions],
    ) -> RequestContextManager:
        """
        Make an HTTP request using the specified method and URL.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE, etc.).
            url: The URL to send the request to. (If base_url is set, this can be relative)
            **kwargs: Additional request options.
        Returns:
            _RequestContextManager object containing the server's response.

        Raises:
            RuntimeError: If the session is not initialized.
        """
        headers = {
            **self._base_headers,
            **(kwargs.get("headers") or {}),
        }
        if "User-Agent" not in headers and "user-agent" not in headers:  # type: ignore
            headers["User-Agent"] = self._user_agent  # type: ignore
        kwargs["headers"] = headers

        coro = self.session.request(method, url, **kwargs).__aenter__()
        return RequestContextManager(coro, str(url), limiter=self._limiter)

    def get(
        self, url: StrOrURL, **kwargs: Unpack[_RequestOptions]
    ) -> RequestContextManager:
        """Perform an HTTP GET request."""
        return self.request("GET", url, **kwargs)

    def post(self, url: StrOrURL, **kwargs: Unpack[_RequestOptions]):
        """Perform an HTTP POST request."""
        return self.request("POST", url, **kwargs)

    def put(
        self, url: StrOrURL, **kwargs: Unpack[_RequestOptions]
    ) -> RequestContextManager:
        """Perform an HTTP PUT request."""
        return self.request("PUT", url, **kwargs)

    def patch(
        self, url: StrOrURL, **kwargs: Unpack[_RequestOptions]
    ) -> RequestContextManager:
        """Perform an HTTP PATCH request."""
        return self.request("PATCH", url, **kwargs)

    def delete(
        self, url: StrOrURL, **kwargs: Unpack[_RequestOptions]
    ) -> RequestContextManager:
        """Perform an HTTP DELETE request."""
        return self.request("DELETE", url, **kwargs)

    def head(
        self, url: StrOrURL, **kwargs: Unpack[_RequestOptions]
    ) -> RequestContextManager:
        """Perform an HTTP HEAD request."""
        return self.request("HEAD", url, **kwargs)

    def options(
        self, url: StrOrURL, **kwargs: Unpack[_RequestOptions]
    ) -> RequestContextManager:
        """Perform an HTTP OPTIONS request."""
        return self.request("OPTIONS", url, **kwargs)

    # === Utility Methods ===
    def _ensure_session(self) -> None:
        """
        Ensure that the session is initialized and not closed.

        Raises:
            RuntimeError: If the session is not initialized or has been closed.
        """
        if self._session is None or self._session.closed:
            raise RuntimeError(
                "Session is not initialized. Use 'async with' context manager."
            )

    async def create_session(self) -> None:
        """
        Create and configure the aiohttp ClientSession.

        Initializes a new session if one doesn't exist or if the existing session is closed.
        """
        if self._session is None or self._session.closed:
            self._session = ClientSession(
                base_url=self._base_url,
                timeout=self._timeout,
                proxy=self._proxy,
                connector=TCPConnector(ssl=not self._disable_ssl),
                trust_env=True,  # Allow using environment variables for proxy settings
            )

            if self._disable_ssl:
                self._session._ssl = False

    async def close(self) -> None:
        """
        Close the HTTP session and release all resources.

        Should be called when the client is no longer needed. Automatically called
        when using the async context manager.
        """
        if self._session and not self._session.closed:
            await self._session.close()

    async def __aenter__(self):
        """
        Enter the async context manager.

        Creates and initializes the HTTP session.

        Returns:
            Self instance with initialized session.
        """
        await self.create_session()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        """
        Exit the async context manager.

        Closes the HTTP session and releases resources.

        Args:
            exc_type: Exception type if an exception was raised.
            exc_value: Exception instance if an exception was raised.
            traceback: Traceback object if an exception was raised.
        """
        await self.close()
