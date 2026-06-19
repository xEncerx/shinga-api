from src.infrastructure.sources.base_provider import BaseProvider
from src.infrastructure.sources.source_headers_loader import SourceHeadersLoader
from src.domain.models.source import Source

from typing import Type


class SourceManager:
    """
    Manager of HTTP clients for providers in long-lived workers.
    Creates one ClientSession per provider during worker initialization and reuses them for all tasks.

    Example usage:
    ```
    source_manager = SourceManager(providers={Source.CUSTOM: CustomClient})

    await source_manager.initialize()

    client = source_manager.get_provider(Source.CUSTOM)
    await client.do_something()

    await source_manager.dispose()
    ```
    """

    def __init__(
        self,
        providers: dict[Source, Type[BaseProvider]],
        base_proxy: str | None = None,
        base_timeout: float = 10,
        headers_loader: SourceHeadersLoader | None = None,
    ) -> None:
        """
        Initialize the SourceManager with provider classes.

        Args:
            providers (dict[Source, Type[BaseProvider]]): A mapping of Source enum to provider classes.
            base_proxy (str | None): Optional base proxy URL for all providers.
            base_timeout (float): Base timeout for all providers. Defaults to 10 seconds.
            headers_loader (SourceHeadersLoader | None): Optional loader for per-source headers.
        """
        self._provider_classes = providers

        self._providers: dict[Source, BaseProvider] = {}
        self._base_proxy = base_proxy
        self._base_timeout = base_timeout
        self._headers_loader = headers_loader
        self._initialized = False

    async def initialize(self) -> None:
        """Initialize all providers by creating their ClientSession instances."""

        if self._initialized:
            return

        for source, provider_class in self._provider_classes.items():
            headers = self._headers_loader.load(source) if self._headers_loader else None
            provider = provider_class(
                timeout=self._base_timeout,
                proxy=self._base_proxy,
                headers=headers,
            )
            await provider.__aenter__()

            self._providers[source] = provider

        self._initialized = True

    async def dispose(self) -> None:
        """Dispose all providers by closing their ClientSession instances."""

        if not self._initialized:
            return

        for provider in self._providers.values():
            await provider.__aexit__(None, None, None)

        self._providers.clear()
        self._initialized = False

    def get_provider(self, source: Source) -> BaseProvider:
        """Get the provider instance for the given source."""

        if not self._initialized:
            raise RuntimeError(
                "ProviderManager not initialized. Call initialize() first."
            )

        provider = self._providers.get(source)
        if not provider:
            raise ValueError(f"Provider for source {source.name} not found.")

        return provider
