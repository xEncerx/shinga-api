import aiohttp

from .base import BaseValueManager, logger


class ProxyManager(BaseValueManager):
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
        validation_timeout: int = 2,
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
        super().__init__(
            validation_interval=validation_interval,
            fetch_interval=fetch_interval,
            batch_validation=batch_validation,
            batch_size=batch_size,
        )

        self.validation_timeout = validation_timeout
        self.test_url = test_url

        self.session_http = aiohttp.ClientSession(
            connector=aiohttp.TCPConnector(ssl=False)
        )
        self.session_http._ssl = False

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
            async with self.session_http.get(
                self.test_url,
                proxy=value,
                timeout=self.validation_timeout, # type: ignore
            ) as response:
                return response.status == 200
        except:
            return False

    async def cleanup(self):
        await self.session_http.close()
        return await super().cleanup()

    async def _fetch_from_public_proxy_list(self, url: str) -> list[str]:
        """Fetch proxies from public proxy list"""
        proxies = []

        try:
            async with self.session_http.get(
                url, timeout=aiohttp.ClientTimeout(total=15)
            ) as response:
                response.raise_for_status()

                content = await response.text()
                for line in content.splitlines():
                    if ":" not in line: continue
                    if line.startswith("http://"):
                        proxies.append(line.strip())
                    elif line:
                        proxies.append(f"http://{line.strip()}")
        except Exception as e:
            logger.error(f"Error fetching from {url}: {e}")

        return proxies
