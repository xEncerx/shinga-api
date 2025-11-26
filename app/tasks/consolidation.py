from annotated_types import T
from celery import Task

from app.domain.services.consolidation.consolidator import ConsolidationService
from app.infrastructure.db.crud import TitleSourceDataCRUD
from app.infrastructure.db.session import get_session
from .event_loop_controller import execute_async_task
from app.domain.enums import ConsolidationStatus
from app.core.celery_config import celery_app
from app.domain.models import TitleData
from app.core import logger


class BaseConsolidationTask(Task):
    """
    Base class for consolidation tasks.
    """

    autoretry_for = (Exception,)
    retry_kwargs = {"max_retries": 2, "countdown": 300}
    retry_backoff = True


@celery_app.task(
    name="app.tasks.consolidation.consolidate_all",
    base=BaseConsolidationTask,
    bind=True,
)
def consolidate_all(
    self,
    batch_size: int = 100,
) -> dict:
    """
    Main task for consolidating unmapped sources.

    Args:
        batch_size (int): Batch size for each subtask. Defaults to 100.

    Returns:
        dict: Statistics dictionary.
    """
    try:
        logger.info("=== CONSOLIDATION ALL STARTED ===")

        async def run():
            total_stats = {
                "consolidation_tasks": 0,
            }

            logger.info("Scheduling consolidation tasks")

            await TitleSourceDataCRUD.update.all_stuck_in_progress()

            while True:
                async with get_session() as session:
                    ids = await TitleSourceDataCRUD.read.claim_unmapped_ids(
                        session=session,
                        fetch_size=batch_size,
                    )

                    if not ids:
                        logger.info("No more unmapped sources")
                        break

                    consolidate_batch.apply_async(
                        kwargs={"source_data_ids": ids},
                        priority=5,
                    )

                    total_stats["consolidation_tasks"] += 1
                    logger.info(
                        f"Dispatched consolidation batch #{total_stats['consolidation_tasks']} with {len(ids)} items"
                    )

            logger.info(f"Consolidation planning complete: {total_stats}")
            return total_stats

        result = execute_async_task(run())
        return result

    except Exception as e:
        logger.error(f"consolidate_all failed: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
        }


@celery_app.task(
    name="app.tasks.consolidation.consolidate_batch",
    base=BaseConsolidationTask,
    bind=True,
)
def consolidate_batch(self, source_data_ids: list[int]) -> dict:
    """
    Consolidate a batch of IN_PROGRESS sources.

    Args:
        source_data_ids (list[int]): List of source IDs for consolidation.

    Returns:
        dict: Processing statistics dictionary.
    """
    try:
        logger.info(f"Processing batch of {len(source_data_ids)} IN_PROGRESS sources")

        async def run():
            async with get_session() as session:
                consolidator = ConsolidationService(session)
                title_data_list = []

                for source_id in source_data_ids:
                    source_data = await TitleSourceDataCRUD.read.source_data_by_id(
                        session=session,
                        id=source_id,
                    )
                    if not source_data:
                        logger.error(f"Source data with ID {source_id} not found")
                        continue

                    try:
                        title_data = TitleData.from_raw_dict(source_data.raw_data)
                        title_data_list.append((title_data, source_data.id))
                    except Exception as e:
                        logger.error(
                            f"Error parsing source data {source_data.id}: {e}",
                            exc_info=True,
                        )

                        await TitleSourceDataCRUD.update.consolidation_status(
                            session=session,
                            source_data_id=source_id,
                            status=ConsolidationStatus.FAILED,
                            parse_error=str(e)[:500],
                        )
                        continue

                if not title_data_list:
                    logger.warning("No valid title data in batch")
                    return {"success": False, "error": "No valid title data"}

                batch_stats = await consolidator.consolidate_batch(
                    title_data_list=title_data_list,
                )

                return batch_stats

        result = execute_async_task(run())
        return result
    except Exception as e:
        logger.error(f"consolidate_batch failed: {e}", exc_info=True)

        return {
            "success": False,
            "error": str(e),
        }
