from app.utils.async_http_client import AsyncHttpClient, ClientTimeout
from .base import BaseValueManager, logger


class ProxyManager(BaseValueManager, AsyncHttpClient):
    """
    Proxy manager that handles proxy fetching, validation, and rate limiting.

    This manager:
    - Fetches proxies from free proxy sources
    - Validates proxies by making test requests
    - Manages rate limits per proxy
    - Automatically removes invalid proxies
    """

    def __init__(
        self,
        validation_interval: int = 300,
        fetch_interval: int = 600,
        batch_validation: bool = True,
        batch_size: int = 1000,
        validation_timeout: int = 3,
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

        self.test_url = test_url

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
            # Fetch from free proxy list APIs
            # proxies.extend(await self._fetch_from_geonode())
            # proxies.extend(
            #     await self._fetch_from_public_proxy_list(
            #         "https://raw.githubusercontent.com/proxifly/free-proxy-list/refs/heads/main/proxies/all/data.txt"
            #     )
            # )
            # proxies.extend(
            #     await self._fetch_from_public_proxy_list(
            #         "https://pastebin.com/raw/mr0Nxai6"
            #     )
            # )

            # Remove duplicates
            proxies = list(set(proxies))

        except Exception as e:
            print(f"Error fetching proxies: {e}")

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
                self.test_url,
                proxy=value,
                response_type="text",
            )
            return True if response else False
        except Exception as e:
            return False

    async def cleanup(self):
        await self.http_client.close()
        return await super().cleanup()

    async def _fetch_from_public_proxy_list(self, url: str) -> list[str]:
        """Fetch proxies from public proxy list"""
        proxies = []

        try:
            response = await self.get(
                url=url,
                response_type="text",
                timeout=ClientTimeout(total=15)
            )
            for line in response.splitlines():
                if ":" not in line:
                    continue
                if line.startswith("http://"):
                    proxies.append(line.strip())
                elif line:
                    proxies.append(f"http://{line.strip()}")
        except Exception as e:
            logger.error(f"Error fetching from {url}: {e}")

        return proxies
