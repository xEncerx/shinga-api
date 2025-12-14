from celery import Task

from app.domain.services.consolidation.title_updater import TitleUpdateService
from app.infrastructure.db.crud.title import TitleCRUD
from app.infrastructure.db.session import get_session
from .event_loop_controller import execute_async_task
from app.core.celery_config import celery_app
from app.core import logger


class BaseRefreshTitlesTask(Task):
    """
    Base class for refresh titles tasks.
    """

    autoretry_for = (Exception,)
    retry_kwargs = {"max_retries": 2, "countdown": 300}
    retry_backoff = True


@celery_app.task(
    name="app.tasks.refresh_titles.refresh_all",
    base=BaseRefreshTitlesTask,
    bind=True,
)
def refresh_all(
    self,
    update_window_hours: int = 168,
    batch_size: int = 100,
) -> dict:
    """
    Main task for refreshing existing titles by re-merging data from all sources.

    Args:
        update_window_hours (int): Time window in hours for finding updated records. Defaults to 54.
        batch_size (int): Batch size for each subtask. Defaults to 100.

    Returns:
        dict: Statistics dictionary.
    """
    try:
        logger.info("=== REFRESH ALL TITLES STARTED ===")

        async def run():
            total_stats = {
                "refresh_tasks": 0,
            }
            cursor_id = 0

            logger.info("Scheduling refresh tasks")

            while True:
                async with get_session() as session:
                    ids = await TitleCRUD.read.claim_for_update(
                        session=session,
                        hours=update_window_hours,
                        fetch_size=batch_size,
                        last_id=cursor_id,
                    )

                    if not ids:
                        logger.info("No more titles to refresh")
                        break

                    cursor_id = ids[-1]

                    refresh_titles_batch.apply_async(
                        kwargs={"title_ids": ids},
                        priority=5,
                    )

                    total_stats["refresh_tasks"] += 1
                    logger.info(
                        f"Dispatched refresh batch #{total_stats['refresh_tasks']} with {len(ids)} items (last_id: {cursor_id})"
                    )

                    if len(ids) < batch_size:
                        logger.info("Reached end of titles (partial batch)")
                        break

            logger.info(f"Refresh planning complete: {total_stats}")
            return total_stats

        result = execute_async_task(run())
        return result

    except Exception as e:
        logger.error(f"refresh_all_titles failed: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
        }


@celery_app.task(
    name="app.tasks.refresh_titles.refresh_batch",
    base=BaseRefreshTitlesTask,
    bind=True,
)
def refresh_titles_batch(self, title_ids: list[int]) -> dict:
    """
    Refresh a batch of existing titles by re-merging their source data.

    Args:
        title_ids (list[int]): List of title IDs to update.

    Returns:
        dict: Processing statistics dictionary.
    """
    try:
        logger.info(f"Refreshing batch of {len(title_ids)} titles")

        async def run():
            async with get_session() as session:
                title_updater = TitleUpdateService(session)
                updated_count = 0
                error_count = 0

                for title_id in title_ids:
                    try:
                        success = await title_updater.update_title(
                            master_title_id=title_id,
                        )

                        if success:
                            updated_count += 1
                        else:
                            error_count += 1

                    except Exception as e:
                        logger.error(
                            f"Error refreshing title {title_id}: {e}",
                            exc_info=True,
                        )
                        error_count += 1
                        continue

                return {
                    "total_updated": updated_count,
                    "total_errors": error_count,
                }

        result = execute_async_task(run())
        return result
    except Exception as e:
        logger.error(f"refresh_titles_batch failed: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
        }
