from taskiq.schedule_sources import LabelScheduleSource
from taskiq import TaskiqScheduler

from .broker import parsing_broker

__all__ = ["scheduler"]

scheduler = TaskiqScheduler(
    broker=parsing_broker,
    sources=[LabelScheduleSource(parsing_broker)],
)
