from celery.signals import worker_process_init, beat_init
from celery.schedules import crontab
from kombu import Queue, Exchange
from celery import Celery
import os

from app.core.logging import setup_logging
from app.core import settings

# Initialize Celery application
celery_app = Celery(
    "shinga_api",
    broker=f"redis://:{settings.REDIS_PASSWORD}@{settings.REDIS_HOST}:{settings.REDIS_PORT}/1",
    backend=f"redis://:{settings.REDIS_PASSWORD}@{settings.REDIS_HOST}:{settings.REDIS_PORT}/2",
)


# === LOGGING SETUP ===
# Worker process logging
@worker_process_init.connect
def setup_worker_logger(sender=None, **kwargs):
    queue_name = os.getenv("CELERY_QUEUE_NAME", "worker")
    setup_logging(f"celery-{queue_name}")


# Beat
@beat_init.connect
def setup_beat_logger(sender=None, **kwargs):
    setup_logging("celery-beat")


# === MAIN CONFIGURATION ===
celery_app.conf.update(
    # === Serialization ===
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Europe/Moscow",
    enable_utc=True,
    # === Results ===
    result_expires=3600,  # 1 hour
    result_backend_transport_options={
        "visibility_timeout": 3600,
    },
    # === Broker connection ===
    broker_connection_retry=True,
    broker_connection_retry_on_startup=True,
    broker_connection_max_retries=10,
    broker_heartbeat=30,
    # === Task routing ===
    task_routes={
        "app.tasks.scraping.*": {"queue": "scraping"},
        "app.tasks.consolidation.*": {"queue": "consolidation"},
        "app.tasks.monitoring.*": {"queue": "monitoring"},
        "app.tasks.refresh_titles.*": {"queue": "refresh_titles"},
        "app.tasks.download_media.*": {"queue": "download_media"},
    },
    # === Retry ===
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    task_autoretry_for=(Exception,),
    task_max_retries=3,
    # === Rate limits ===
    task_annotations={
        "app.tasks.scraping.scrape_source": {
            "rate_limit": "50/m",
        },
        "app.tasks.consolidation.consolidate_all": {
            "time_limit": 24 * 60 * 60,  # 24 hours
        },
        "app.tasks.download_media.cover": {
            "rate_limit": "400/m",
        },
    },
    # === Worker settings ===
    worker_prefetch_multiplier=4,
    worker_max_tasks_per_child=1000,
    worker_disable_rate_limits=False,
    # === Logging ===
    worker_hijack_root_logger=False,
    worker_log_color=False,
    worker_log_level="ERROR",
    # === Monitoring ===
    worker_send_task_events=True,
    task_send_sent_event=True,
    # === Imports ===
    imports=[
        "app.tasks.scraping",
        "app.tasks.consolidation",
        "app.tasks.refresh_titles",
        "app.tasks.monitoring",
        "app.tasks.download_media",
    ],
)

# === QUEUES ===
celery_app.conf.task_queues = (
    Queue(
        "scraping",
        Exchange("scraping", type="direct"),
        routing_key="scraping",
        queue_arguments={"x-max-priority": 10},
        priority=10,
    ),
    Queue(
        "consolidation",
        Exchange("consolidation", type="direct"),
        routing_key="consolidation",
        queue_arguments={"x-max-priority": 8},
        priority=8,
    ),
    Queue(
        "refresh_titles",
        Exchange("refresh_titles", type="direct"),
        routing_key="refresh_titles",
        queue_arguments={"x-max-priority": 7},
        priority=7,
    ),
    Queue(
        "download_media",
        Exchange("download_media", type="direct"),
        routing_key="download_media",
        queue_arguments={"x-max-priority": 5},
        priority=5,
    ),
    Queue(
        "monitoring",
        Exchange("monitoring", type="direct"),
        routing_key="monitoring",
        priority=1,
    ),
)

# === SCHEDULE (BEAT) ===
celery_app.conf.beat_schedule = {
    # Full parsing of all sources twice a week at 02:00 on Monday and Thursday
    "scrape-all-sources": {
        "task": "app.tasks.scraping.scrape_all_sources",
        "schedule": crontab(hour=2, minute=0, day_of_week="1,4"),
        "options": {
            "priority": 10,
            "queue": "scraping",
        },
    },
    # Consolidation at 08:00 on Saturday
    "consolidate-titles": {
        "task": "app.tasks.consolidation.consolidate_all",
        "schedule": crontab(hour=8, minute=0, day_of_week="6"),  # 6 = Saturday
        "options": {
            "priority": 8,
            "queue": "consolidation",
        },
    },
    # Refresh existing titles at 08:00 on Sunday
    "refresh-titles": {
        "task": "app.tasks.refresh_titles.refresh_all",
        "schedule": crontab(hour=8, minute=0, day_of_week="0"),  # 0 = Sunday
        "options": {
            "priority": 7,
            "queue": "refresh_titles",
        },
    },
    # Collect statistics every hour
    "collect-statistics": {
        "task": "app.tasks.monitoring.collect_statistics",
        "schedule": crontab(minute=0),
        "options": {
            "priority": 1,
            "queue": "monitoring",
        },
    },
}
