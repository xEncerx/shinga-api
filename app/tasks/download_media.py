from celery import Task

from app.infrastructure.db.models.title.relations import TitleCover
from app.infrastructure.managers.media_manager import MediaManger
from .event_loop_controller import execute_async_task
from app.infrastructure.db.crud import TitleCRUD
from app.core.celery_config import celery_app
from app.core import settings, logger


class BaseCoverTask(Task):
    """
    Base class for cover download tasks.
    """

    autoretry_for = (ValueError, Exception)
    retry_kwargs = {"max_retries": 3, "countdown": 60}
    retry_backoff = True


@celery_app.task(
    name="app.tasks.download_media.cover",
    base=BaseCoverTask,
    bind=True,
)
def download_cover_task(
    self,
    title_id: int,
    cover_url: str,
    source_provider: str,
) -> dict:
    """
    Task for downloading a title cover.

    Args:
        title_id (int): Title ID.
        cover_url (str): Cover URL.
        source_provider (str): Source provider name.

    Returns:
        dict: Result dictionary.
    """

    async def run():
        if not title_id:
            logger.warning("No title_id provided for cover download task")
            return {"success": False, "error": "No title_id provided"}

        covers = await MediaManger().save_cover(
            image_url=cover_url,
            provider=source_provider,
            content_id=str(title_id),
        )

        await TitleCRUD.update.title_cover(
            title_id=title_id,
            cover=TitleCover(
                url=covers[0],
                small_url=covers[1],
                large_url=covers[2],
            ),
        )

        if covers[0] == settings.COVER_404_PATH:
            raise ValueError(f"Cover download resulted in 404 image for title_id={title_id}")

        logger.info(f"Cover downloaded for title_id={title_id}: {covers[0]}")

        return {
            "success": True,
            "title_id": title_id,
        }

    result = execute_async_task(run())
    return result
