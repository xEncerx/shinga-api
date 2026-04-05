from taskiq import Context, TaskiqDepends

from typing import Annotated

from src.application.use_cases import UpdateMasterTitleUseCase, MergeMasterTitlesUseCase
from src.infrastructure.db.repositories import TitleRepository
from src.infrastructure.tasks.broker import parsing_broker
from src.core import logger


@parsing_broker.task(
    schedule=[
        {
            "cron": "0 4 * * 0",  # Sun=0
            "schedule_id": "update_schedule",
        }
    ]
)
async def enqueue_update_jobs_task(
    context: Annotated[Context, TaskiqDepends()],
):
    """
    Scheduled: Enqueues update jobs for stale master titles.
    Queries master titles requiring updates and kicks update_master_title_task.

    Runs every Sunday at 04:00 UTC.
    """
    cursor_id = 0
    async with context.state.session_factory() as session:
        title_repo = TitleRepository(session)
        while True:
            master_title_ids = await title_repo.get_master_title_for_update(
                limit=100,
                last_id=cursor_id,
            )

            for master_title_id in master_title_ids:
                await update_master_title_task.kiq(
                    master_title_id=master_title_id,
                )  # type: ignore

            if len(master_title_ids) < 100:
                break

            cursor_id = master_title_ids[-1]


@parsing_broker.task
async def update_master_title_task(
    master_title_id: int,
    context: Annotated[Context, TaskiqDepends()],
):
    """Task: Updates a specific master title"""

    try:
        async with context.state.session_factory() as session:
            repo = TitleRepository(session)
            use_case = UpdateMasterTitleUseCase(
                title_repository=repo,
                title_merge_use_case=MergeMasterTitlesUseCase(
                    title_repository=repo
                ),
            )

            async with session.begin():
                await use_case.execute(master_title_id)

        logger.info("Updated master title ID={} successfully.", master_title_id)
    except Exception as e:
        logger.error(
            "Unexpected error updating master title ID={}: {}",
            master_title_id,
            e,
        )
        return None
