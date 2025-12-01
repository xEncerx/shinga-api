from celery import Task, group
from typing import Any

from app.domain.models.exceptions import RateLimitError, ProviderUnavailableError
from app.infrastructure.scraping.page_queue_builder import PageQueueBuilder
from app.infrastructure.scraping.scraping_manager import ScrapingManager
from app.infrastructure.db.session import get_session
from .event_loop_controller import execute_async_task
from app.providers.base_provider import BaseProvider
from app.core.celery_config import celery_app
from app.domain.enums import SourceProvider
from app.core import logger
from app.providers import *


class BaseScrapingTask(Task):
    """
    Base class for scraping tasks with error handling.
    """

    autoretry_for = (
        RateLimitError,
        ProviderUnavailableError,
    )
    retry_kwargs = {"max_retries": 5}
    retry_backoff = True
    retry_backoff_max = 600  # 10 minutes
    retry_jitter = True  # Add random delay

    def retry(self, args=None, kwargs=None, exc=None, **options):
        """Custom retry logic based on exception type."""
        if isinstance(exc, RateLimitError) and exc.retry_after:
            options["countdown"] = exc.retry_after
            logger.info(f"Rate limit hit, retrying after {exc.retry_after}s")
        elif isinstance(exc, RateLimitError):
            options["countdown"] = 60 * (2**self.request.retries)
        elif isinstance(exc, ProviderUnavailableError):
            options["countdown"] = 30 * (2**self.request.retries)

        return super().retry(args, kwargs, exc, **options)


# === PROVIDER MAPPING ===
PROVIDER_MAP: dict[SourceProvider, type[BaseProvider]] = {
    SourceProvider.MAL: MalProvider,
    SourceProvider.SHIKIMORI: ShikimoriProvider,
    SourceProvider.REMANGA: RemangaProvider,
}


@celery_app.task(name="app.tasks.scraping.scrape_all_sources", bind=True)
def scrape_all_sources(self) -> dict:
    """
    Main task: scrape all sources.

    Orchestrates the entire process:
    1. Gets page queues for each provider
    2. Launches scraping for each provider
    3. After completion - launches consolidation

    Returns:
        dict: Statistics dictionary.
    """
    try:
        logger.info("=== SCRAPING ALL SOURCES STARTED ===")

        async def run():
            queue_builder = PageQueueBuilder()
            queues = {}

            for source_provider, provider_class in PROVIDER_MAP.items():
                try:
                    async with provider_class() as provider_instance:
                        page_queue, provider_config = (
                            await queue_builder.build_queue_for_provider(
                                provider=provider_instance,
                                source_provider=source_provider,
                            )
                        )

                        if page_queue:
                            queues[source_provider] = (page_queue, provider_config)
                            logger.info(
                                f"Queue built for {source_provider.value}: {len(page_queue)} pages"
                            )
                except Exception as e:
                    logger.error(
                        f"Failed to build queue for {source_provider.value}: {e}",
                        exc_info=True,
                    )
                    continue

            if not queues:
                logger.error("No queues built for any provider")
                return {
                    "success": False,
                    "error": "No queues built",
                }

            scraping_tasks = []
            for source_provider, (page_queue, provider_config) in queues.items():
                page_tasks = [
                    scrape_source.si(
                        source_provider=source_provider.value,
                        page_number=page_num,
                        provider_config=provider_config,
                    )
                    for page_num in page_queue
                ]

                scraping_tasks.extend(page_tasks)

            if scraping_tasks:
                logger.info(f"Queuing {len(scraping_tasks)} scraping tasks")

                job = group(*scraping_tasks)
                result = job.apply_async(queue="scraping", priority=10)

                logger.info(f"Scraping tasks queued: {result.id}")

                return {
                    "success": True,
                    "total_tasks": len(scraping_tasks),
                    "providers": list(queues.keys()),
                    "task_group_id": str(result.id),
                }

            return {
                "success": False,
                "error": "No scraping tasks created",
            }

        result = execute_async_task(run())
        return result

    except Exception as e:
        logger.error(f"scrape_all_sources failed: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
        }


@celery_app.task(
    name="app.tasks.scraping.scrape_source",
    base=BaseScrapingTask,
    bind=True,
)
def scrape_source(
    self,
    source_provider: str,
    page_number: int,
    provider_config: dict[str, Any],
) -> dict:
    """
    Scrape a single page from a provider.

    Args:
        source_provider (str): SourceProvider enum string.
        page_number (int): Page number to scrape.
        provider_config (dict[str, Any]): Provider configuration dictionary.

    Returns:
        dict: Statistics dictionary.
    """
    try:
        logger.info(f"Scraping page {page_number} from {source_provider}")

        try:
            source_enum = SourceProvider[source_provider.upper()]
        except KeyError:
            logger.error(f"Unknown source provider: {source_provider}")
            return {
                "success": False,
                "error": f"Unknown provider: {source_provider}",
            }

        if source_enum not in PROVIDER_MAP:
            logger.error(f"Provider not configured: {source_provider}")
            return {
                "success": False,
                "error": f"Provider not configured: {source_provider}",
            }

        provider_class = PROVIDER_MAP[source_enum]

        async def run():
            async with get_session() as session, provider_class() as provider:
                scraping_manager = ScrapingManager(
                    session=session,
                    provider=provider,
                    source_provider=source_enum,
                    provider_config=provider_config,
                )

                titles, success = await scraping_manager.scrape_page(
                    page_number=page_number
                )

                if success:
                    return {
                        "success": True,
                        "provider": source_provider,
                        "page": page_number,
                        "titles_scraped": len(titles),
                    }
                else:
                    return {
                        "success": False,
                        "provider": source_provider,
                        "page": page_number,
                        "error": "Scraping failed",
                    }

        result = execute_async_task(run())
        return result

    except (RateLimitError, ProviderUnavailableError):
        raise  # re-raise for auto-retry

    except Exception as e:
        logger.error(f"scrape_source task failed: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
        }
