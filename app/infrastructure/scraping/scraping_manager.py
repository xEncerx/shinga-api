from sqlmodel.ext.asyncio.session import AsyncSession
from typing import Any, Optional

from app.infrastructure.db.crud import TitleSourceDataCRUD
from app.providers.base_provider import BaseProvider
from app.domain.enums import SourceProvider
from app.domain.models import TitleData
from app.core import logger


class ScrapingManager:
    """
    Scraping manager for a single provider.
    """

    def __init__(
        self,
        session: AsyncSession,
        provider: BaseProvider,
        source_provider: SourceProvider,
        provider_config: dict[str, Any],
    ):
        """
        Initialize the scraping manager.

        Args:
            session (AsyncSession): Async SQLModel session.
            provider (BaseProvider): Provider instance for fetch_page.
            source_provider (SourceProvider): Provider enum.
            provider_config (dict[str, Any]): Provider configuration dictionary.
        """
        self.session = session
        self.provider = provider
        self.source_provider = source_provider
        self.provider_config = provider_config

    async def scrape_page(
        self,
        page_number: int,
        proxy: Optional[str] = None,
    ) -> tuple[list[TitleData], bool]:
        """
        Scrape a single page and save to the database.

        Args:
            page_number (int): Page number to scrape.
            proxy (Optional[str]): Optional proxy string. Defaults to None.

        Returns:
            tuple[list[TitleData], bool]: Tuple of (list of TitleData, success flag).
        """
        logger.debug(
            f"ScrapingManager: Fetching page {page_number} "
            f"from {self.source_provider.value}"
        )

        pagination = await self.provider.get_page(
            page=page_number,
            proxy=proxy,
            **self.provider_config,
        )

        if not pagination or not pagination.data:
            logger.warning(
                f"ScrapingManager: Empty page {page_number} "
                f"from {self.source_provider.value}"
            )
            return [], False

        title_data_list = pagination.data

        logger.debug(
            f"ScrapingManager: Parsing {len(title_data_list)} titles "
            f"from page {page_number}"
        )

        created_count = 0
        for title_data in title_data_list:
            try:
                await TitleSourceDataCRUD.create.title_source_data(
                    session=self.session,
                    source_provider=self.source_provider,
                    source_id=title_data.source_id,
                    title_data=title_data,
                    source_url=title_data.source_url,
                )
                created_count += 1
            except Exception as e:
                await self.session.rollback()
                logger.error(
                    f"Error saving title {title_data.source_id} "
                    f"from {self.source_provider.value}: {e}"
                )
                continue

        logger.info(
            f"ScrapingManager: Page {page_number} complete - "
            f"{created_count}/{len(title_data_list)} titles saved "
            f"({self.source_provider.value})"
        )

        return title_data_list, True
