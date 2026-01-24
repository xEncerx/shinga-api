from taskiq import Context, TaskiqDepends

from typing import Annotated

from src.application.tasks.media_tasks import download_cover_task
from src.application.services.matchers import AVAILABLE_MATCHERS
from src.application.use_cases import ConsolidateRawTitleUseCase
from src.infrastructure.db.repositories import TitleRepository
from src.domain.models.services import ConsolidationStatus
from src.infrastructure.tasks.broker import broker
from src.core import logger


@broker.task(
    schedule=[
        {
            "cron": "0 3 * * 6",  # Sat=6
            "schedule_id": "consolidation_schedule",
        }
    ]
)
async def enqueue_consolidation_jobs_task(
    context: Annotated[Context, TaskiqDepends()],
):
    """
    Scheduled: Enqueues consolidation jobs for pending raw titles.
    Queries raw titles with PENDING status and kicks consolidate_raw_title_task.

    Runs every Saturday at 03:00 UTC.
    """
    async with context.state.session_factory() as session:
        title_repo = TitleRepository(session)
        while True:
            async with session.begin():
                raw_title_ids = await title_repo.get_unmapped_raw_titles(limit=100)

            for raw_title_id in raw_title_ids:
                await consolidate_raw_title_task.kiq(
                    raw_title_id=raw_title_id,
                )  # type: ignore

            if len(raw_title_ids) < 100:
                break


@broker.task
async def consolidate_raw_title_task(
    raw_title_id: int,
    context: Annotated[Context, TaskiqDepends()],
):
    """
    Task: Consolidates a raw title by normalizing and deduplicating it.
    """
    try:
        async with context.state.session_factory() as session:
            title_repo = TitleRepository(session)
            use_case = ConsolidateRawTitleUseCase(
                title_repository=title_repo,
                matchers=[mc(title_repo) for mc in AVAILABLE_MATCHERS],
            )

            try:
                async with session.begin():
                    result = await use_case.execute(raw_title_id)
            except Exception as e:
                # On any error, update status to FAILED with error detail
                async with session.begin():
                    await title_repo.update_consolidation_status(
                        status=ConsolidationStatus.FAILED,
                        raw_title_id=raw_title_id,
                        detail=str(e),
                    )
                raise e

        if result.cover_url:
            # Trigger cover download task
            await download_cover_task.kiq(
                master_title_id=result.master_title_id,
                cover_url=result.cover_url,
                source=result.source,
                external_id=result.external_id,
            )  # type: ignore

        logger.info(
            f"[{'NEW' if result.is_new else 'UPDATED'}] Consolidated raw title ID={raw_title_id} into master title ID={result.master_title_id} ({result.source.upper()}:{result.external_id})"
        )
    except Exception as e:
        logger.error(
            f"Unexpected error consolidating raw title ID={raw_title_id}: {e}",
            exc_info=True,
        )
        return None
