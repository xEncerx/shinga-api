from app.utils.async_http_client import AsyncHttpClient, ClientTimeout
from app.core import logger, settings
from .base import BaseValueManager

import aiofiles


class ProxyManager(BaseValueManager, AsyncHttpClient):
    """
    Proxy manager that handles proxy fetching, validation, and rate limiting.

    **SUPPORT ONLY HTTP PROXIES**

    This manager:
    - Fetches proxies from free proxy sources
    - Validates proxies by making test requests
    - Manages rate limits per proxy
    - Automatically removes invalid proxies
    """

    def __init__(
        self,
        validation_interval: int = 1*60*60, # 1 hour
        fetch_interval: int = 2*60*60, # 2 hours
        batch_validation: bool = True,
        batch_size: int = 1000,
        validation_timeout: int = 4,
        test_url: str = "http://example.com",
    ):
        """
        Initialize the proxy manager.

        Args:
            validation_interval: How often to validate proxies (seconds)
            fetch_interval: How often to fetch new proxies (seconds)
            batch_validation: Whether to validate proxies in batches
            batch_size: Size of validation batches
            validation_timeout: Timeout for proxy validation requests
            test_url: URL to use for proxy validation
        """
        BaseValueManager.__init__(
            self,
            validation_interval=validation_interval,
            fetch_interval=fetch_interval,
            batch_validation=batch_validation,
            batch_size=batch_size,
        )
        AsyncHttpClient.__init__(
            self,
            timeout=validation_timeout,
            disable_ssl=True,
        )

        self._test_url = test_url

        self._proxies_file = settings.CORE_PATH / "proxies.txt"

        # Configure rate limits
        # Example: 3 requests per second, 60 requests per minute
        self.add_limit("rps", max_requests=3, time_window=1, cooldown=1)
        self.add_limit("rpm", max_requests=60, time_window=60, cooldown=60)

    async def fetch_values(self) -> list[str]:
        """
        Fetch new proxies from free proxy sources.

        Returns:
            List of proxy strings in format "ip:port"
        """
        proxies = []

        try:
            proxies.extend(await self._fetch_from_file())
            # Remove duplicates
            proxies = list(set(proxies))

        except Exception as e:
            logger.error(f"Error fetching proxies: {e}")

        return proxies

    async def validate_value(self, value: str) -> bool:
        """
        Validate a single proxy by making a test request.

        Args:
            proxy: Proxy string in format "ip:port"

        Returns:
            True if proxy is working, False otherwise
        """
        try:
            response = await self.get(
                self._test_url,
                proxy=value,
                response_type="text",
            )
            return True if response else False
        except Exception as e:
            return False

    async def cleanup(self):
        await self.http_client.close()
        return await super().cleanup()

    async def _fetch_from_file(self) -> list[str]:
        if not self._proxies_file.exists():
            async with aiofiles.open(self._proxies_file, "w") as f:
                await f.write(
                    "# Add your proxies here in the format http://ip:port OR http://username:password@ip:port\n" \
                    "# ONLY HTTP PROXIES ARE SUPPORTED",
                )
            return []

        async with aiofiles.open(self._proxies_file, mode="r") as f:
            content = await f.read()

        proxies = []
        for line in content.splitlines():
            if ":" not in line:
                continue
            if line.startswith("http://"):
                proxies.append(line.strip())

        return proxies
