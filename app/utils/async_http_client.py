from aiohttp.client import _RequestOptions
from aiohttp import (
    ClientSession,
    TCPConnector,
    ClientTimeout,
)
from typing import Unpack, Any, Literal

ResponseType = Literal["json", "text", "bytes", "stream"]


class AsyncHttpClient:
    """
    Asynchronous HTTP client wrapper around aiohttp.ClientSession.
    
    Provides a simplified interface for making HTTP requests with support for
    different response types and common HTTP methods.
    
    Attributes:
        http_client (ClientSession): The underlying aiohttp ClientSession instance.
    """
    
    def __init__(
        self,
        base_url: str | None = None,
        timeout: float = 15.0,
        disable_ssl: bool = False,
        proxy: str | None = None,
    ) -> None:
        """
        Initialize the AsyncHttpClient.
        
        Args:
            base_url (str | None): Base URL for all requests. Defaults to None.
            timeout (float): Request timeout in seconds. Defaults to 15.0.
            disable_ssl (bool): Whether to disable SSL verification. Defaults to False.
            proxy (str | None): Proxy URL to use for requests. Defaults to None.
        """
        self.http_client = ClientSession(
            base_url=base_url,
            timeout=ClientTimeout(total=timeout),
            proxy=proxy,
            connector=TCPConnector(
                ssl=not disable_ssl,
            ),
        )
        if disable_ssl:
            self.http_client._ssl = False

    async def request(
        self,
        method: str,
        url: str,
        response_type: ResponseType = "json",
        **kwargs: Unpack[_RequestOptions],
    ) -> Any:
        """
        Make an HTTP request with the specified method.
        
        Args:
            method (str): HTTP method (GET, POST, PUT, DELETE, PATCH, etc.).
            url (str): Request URL (relative to base_url if set).
            response_type (ResponseType): Type of response to return.
                Options: "json", "text", "bytes", "stream". Defaults to "json".
            **kwargs: Additional request options passed to aiohttp.
            
        Returns:
            Any: Response data in the format specified by response_type.
            
        Raises:
            aiohttp.ClientResponseError: If the response status indicates an error.
            ValueError: If an unsupported response_type is provided.
        """
        async with self.http_client.request(
            method,
            url,
            **kwargs,
        ) as response:
            response.raise_for_status()

            if response_type == "json":
                return await response.json()
            elif response_type == "text":
                return await response.text()
            elif response_type == "bytes":
                return await response.read()
            elif response_type == "stream":
                return await response.read()
            else:
                raise ValueError(f"Unsupported response type: {response_type}")

    async def get(
        self,
        url: str,
        response_type: ResponseType = "json",
        **kwargs: Unpack[_RequestOptions],
    ) -> Any:
        """
        Make a GET request.
        
        Args:
            url (str): Request URL (relative to base_url if set).
            response_type (ResponseType): Type of response to return. Defaults to "json".
            **kwargs: Additional request options passed to aiohttp.
            
        Returns:
            Any: Response data in the format specified by response_type.
        """
        return await self.request(
            "GET",
            url,
            response_type=response_type,
            **kwargs,
        )

    async def post(
        self,
        url: str,
        response_type: ResponseType = "json",
        **kwargs: Unpack[_RequestOptions],
    ) -> Any:
        """
        Make a POST request.
        
        Args:
            url (str): Request URL (relative to base_url if set).
            response_type (ResponseType): Type of response to return. Defaults to "json".
            **kwargs: Additional request options passed to aiohttp.
            
        Returns:
            Any: Response data in the format specified by response_type.
        """
        return await self.request(
            "POST",
            url,
            response_type=response_type,
            **kwargs,
        )

    async def put(
        self,
        url: str,
        response_type: ResponseType = "json",
        **kwargs: Unpack[_RequestOptions],
    ) -> Any:
        """
        Make a PUT request.
        
        Args:
            url (str): Request URL (relative to base_url if set).
            response_type (ResponseType): Type of response to return. Defaults to "json".
            **kwargs: Additional request options passed to aiohttp.
            
        Returns:
            Any: Response data in the format specified by response_type.
        """
        return await self.request(
            "PUT",
            url,
            response_type=response_type,
            **kwargs,
        )

    async def delete(
        self,
        url: str,
        response_type: ResponseType = "json",
        **kwargs: Unpack[_RequestOptions],
    ) -> Any:
        """
        Make a DELETE request.
        
        Args:
            url (str): Request URL (relative to base_url if set).
            response_type (ResponseType): Type of response to return. Defaults to "json".
            **kwargs: Additional request options passed to aiohttp.
            
        Returns:
            Any: Response data in the format specified by response_type.
        """
        return await self.request(
            "DELETE",
            url,
            response_type=response_type,
            **kwargs,
        )

    async def patch(
        self,
        url: str,
        response_type: ResponseType = "json",
        **kwargs: Unpack[_RequestOptions],
    ) -> Any:
        """
        Make a PATCH request.
        
        Args:
            url (str): Request URL (relative to base_url if set).
            response_type (ResponseType): Type of response to return. Defaults to "json".
            **kwargs: Additional request options passed to aiohttp.
            
        Returns:
            Any: Response data in the format specified by response_type.
        """
        return await self.request(
            "PATCH",
            url,
            response_type=response_type,
            **kwargs,
        )

    async def close(self) -> None:
        """
        Close the HTTP client and clean up resources.
        
        This method should be called when you're done using the client
        to properly clean up connections and free resources.
        """
        await self.http_client.close()

    async def __aenter__(self) -> "AsyncHttpClient":
        """
        Async context manager entry.
        
        Returns:
            AsyncHttpClient: Self instance for use in async with statements.
        """
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """
        Async context manager exit.
        
        Automatically closes the HTTP client when exiting the context.
        """
        await self.close()