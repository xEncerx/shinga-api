from taskiq.schedule_sources import LabelScheduleSource
from taskiq import TaskiqScheduler

from .broker import broker

scheduler = TaskiqScheduler(
    broker=broker,
    sources=[LabelScheduleSource(broker)],
)
