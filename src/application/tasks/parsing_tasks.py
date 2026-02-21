from src.infrastructure.network.exceptions import (
    HttpTimeoutError,
    HttpConnectionError,
    HttpServerError,
)
from sqlalchemy.exc import OperationalError, DBAPIError
from asyncio import TimeoutError

from taskiq import Context, TaskiqDepends
from typing import Annotated

from src.infrastructure.sources import AVAILABLE_SOURCES, BaseProvider
from src.infrastructure.sources.base_provider import SourceDetail
from src.infrastructure.db.repositories import TitleRepository
from src.application.use_cases import ParseSourcePageUseCase
from src.infrastructure.tasks.broker import parsing_broker
from src.domain.models.source import Source
from src.core import logger


RETRYABLE_EXCEPTIONS = (
    HttpTimeoutError,
    HttpConnectionError,
    HttpServerError,
    TimeoutError,
    OperationalError,
    DBAPIError,
)


@parsing_broker.task(
    schedule=[
        {
            "cron": "0 2 * * 1,4",  # Mon=1, Thu=4
            "schedule_id": "parsing_schedule",
        }
    ]
)
async def enqueue_parsing_jobs_task(
    context: Annotated[Context, TaskiqDepends()],
):
    """
    Scheduled: Enqueues parsing jobs for all active sources in round-robin order.
    Distributes page parsing tasks across sources to prevent rate limiting.

    Runs every Monday and Thursday at 02:00 UTC.
    """
    if not AVAILABLE_SOURCES:
        logger.warning("No available sources to enqueue parsing jobs")
        return

    # Collect metadata for all sources
    sources_info: list[SourceDetail] = []
    for source in AVAILABLE_SOURCES.keys():
        try:
            source_client: BaseProvider = context.state.source_manager.get_provider(
                source
            )
            source_detail = await source_client.get_source_detail()
            sources_info.append(source_detail)
            logger.info(
                "Source '{}' has {} pages with {} items per page",
                source.name,
                source_detail.total_pages,
                source_detail.items_per_page,
            )
        except Exception as e:
            logger.error(
                "Failed to get source detail for source '{}': {}", source.name, e
            )

    # Find maximum number of pages across all sources
    max_pages = max(info.total_pages for info in sources_info)

    # Enqueue tasks in round-robin order: A-1, B-1, C-1, A-2, B-2, C-2, ...
    for page in range(1, max_pages + 1):
        for source_info in sources_info:
            if page <= source_info.total_pages:
                await parse_source_page_task.kiq(
                    source_info.source,
                    page,
                    source_info.items_per_page,
                )  # type: ignore


@parsing_broker.task(retry_on_error=True)
async def parse_source_page_task(
    source: Source,
    page: int,
    page_size: int,
    context: Annotated[Context, TaskiqDepends()],
):
    """
    Task: Parses a specific page from a given source.
    Fetches content, extracts data, and stores it in the database.
    """
    source_client: BaseProvider = context.state.source_manager.get_provider(source)

    try:
        async with context.state.session_factory() as session:
            use_case = ParseSourcePageUseCase(
                title_repository=TitleRepository(session=session),
                source_client=source_client,
            )

            async with session.begin():
                result = await use_case.execute(page=page, limit=page_size)

        logger.info(
            "Parsed page {}: {}/{} titles from {}",
            page,
            result.upserted,
            page_size,
            source.name,
        )
        if len(result.errors) > 0:
            for err in result.errors:
                logger.error(
                    "Error parsing title on page {} from {}: {}",
                    page,
                    source.name,
                    err,
                )
    except RETRYABLE_EXCEPTIONS as e:
        logger.warning(
            "Retryable error while parsing page {} from source {}: {}",
            page,
            source.name,
            e,
        )
        raise
    except Exception as e:
        logger.error(
            "Unexpected error while parsing page {} from source {}: {}",
            page,
            source.name,
            e,
        )
        return None
