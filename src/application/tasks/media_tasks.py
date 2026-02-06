from src.infrastructure.network.exceptions import (
    HttpTimeoutError,
    HttpConnectionError,
    HttpServerError,
)
from sqlalchemy.exc import OperationalError, DBAPIError
from asyncio import TimeoutError

from taskiq import Context, TaskiqDepends

from typing import Annotated

from src.infrastructure.db.repositories import TitleRepository
from src.application.use_cases import ProcessImageUseCase
from src.infrastructure.tasks.broker import broker
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


@broker.task
async def download_cover_task(
    master_title_id: int,
    cover_url: str,
    source: Source,
    external_id: str,
    context: Annotated[Context, TaskiqDepends()],
):
    """
    Task: Downloads and processes a cover image for a master title.
    Utilizes ProcessImageUseCase to handle downloading, processing, and storing the image.
    """
    try:
        async with context.state.session_factory() as session:
            use_case = ProcessImageUseCase(
                title_repository=TitleRepository(session),
                downloader=context.state.media_downloader,
                storage=context.state.cover_storage,
                processor=context.state.image_processor,
            )

            async with session.begin():
                await use_case.execute(
                    master_title_id=master_title_id,
                    cover_url=cover_url,
                    source=source,
                    external_id=external_id,
                )

        logger.info(
            f"Processed cover: master_title_id={master_title_id}, source={source.name}, external_id={external_id}"
        )
    except RETRYABLE_EXCEPTIONS as e:
        logger.warning(
            f"Retryable error processing cover: master_title_id={master_title_id}, source={source.name}, external_id={external_id}: {e}"
        )
        raise e
    except Exception as e:
        logger.error(
            f"Unexpected error processing cover: master_title_id={master_title_id}, source={source.name}, external_id={external_id}: {e}"
        )
        return None
