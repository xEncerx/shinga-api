from typing import Any

from app.providers.base_provider import BaseProvider
from app.domain.enums import SourceProvider
from app.core import logger


class PageQueueBuilder:
    """
    Page queue builder for scraping.

    Fetches the number of available pages from each provider and creates queues for processing.
    """

    async def build_queue_for_provider(
        self,
        provider: BaseProvider,
        source_provider: SourceProvider,
    ) -> tuple[list[int], dict[str, Any]]:
        """
        Build a page queue for a provider.

        Args:
            provider (BaseProvider): Provider instance.
            source_provider (SourceProvider): Provider enum.

        Returns:
            tuple[list[int], dict[str, Any]]: Tuple of (list of page numbers, scraping config).
        """
        try:
            scraping_config = await provider.get_scraping_config()
            total_pages = scraping_config.get("total_pages", 1)

            logger.info(
                f"PageQueueBuilder: {source_provider.value} - total pages: {total_pages}"
            )

            page_queue = list(range(1, total_pages + 1))

            return page_queue, scraping_config

        except Exception as e:
            logger.error(f"Error building queue for {source_provider.value}: {e}", exc_info=True)
            return [], {}
