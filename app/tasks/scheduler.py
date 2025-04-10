from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.tasks import backup_task, manga_task
from app.core import settings
from app.utils import logger

scheduler = AsyncIOScheduler()


def init_scheduler():
    logger.info("Initializing scheduler...")

    scheduler.add_job(
        backup_task.perform_backup_task,
        settings.BACKUP_TIME,
        max_instances=1,
    )

    scheduler.add_job(
        manga_task.manga_updater_task,
        settings.MANGA_UPDATER_INTERVAL,
        max_instances=1,
    )

    logger.info("Scheduler initialized.")

    scheduler.start()
