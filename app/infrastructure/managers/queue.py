from app.core import logger

from dataclasses import dataclass
from typing import Callable, Any
from enum import Enum
import asyncio


class QueuePriority(int, Enum):
    """Priority levels for queues."""
    HIGH = 1
    MEDIUM = 2
    LOW = 3


@dataclass
class QueueConfig:
    """
    Configuration class for a queue.

    Attributes:
        name: Name of the queue
        priority: Priority level of the queue
        queue: asyncio.Queue object for task management
        handler: Callable function to process tasks from this queue
        min_workers: Minimum number of workers required for this queue
        max_workers: Maximum number of workers allowed for this queue (optional)
    """
    name: str
    priority: QueuePriority
    queue: asyncio.Queue
    handler: Callable
    min_workers: int = 1
    max_workers: int | None = None


class PriorityQueueManager:
    def __init__(self, workers: list[Any], check_interval: float = 0.1):
        """
        Manager for priority queues to distribute tasks among workers.

        Args:
            workers (list[Any]): List of worker instances that will process tasks
            check_interval: Interval in seconds to check the queues and distribute tasks
        """
        self.workers = workers
        self.check_interval = check_interval
        self.queues: dict[str, QueueConfig] = {}
        self.worker_assignments: dict[int, str | None] = {
            i: None for i in range(len(workers))
        }

        self._running = False
        self._monitor_task: asyncio.Task | None = None
        self._max_available_workers = len(workers)

    def register_queue(
        self,
        name: str,
        queue: asyncio.Queue,
        priority: QueuePriority,
        handler: Callable,
        min_workers: int = 1,
        max_workers: int | None = None
    ) -> None:
        """
        Register a new queue with the manager.

        Args:
            name (str): Name of the queue
            queue (asyncio.Queue): Queue object for task management
            priority (QueuePriority): Priority level of the queue
            handler (Callable): Callable function to process tasks from this queue
            min_workers (int): Minimum number of workers required for this queue
            max_workers (int | None): Maximum number of workers allowed for this queue (optional)
        """
        self.queues[name] = QueueConfig(
            name=name,
            priority=priority,
            queue=queue,
            handler=handler,
            min_workers=min_workers,
            max_workers=max_workers,
        )
        logger.info(
            f"{__class__.__name__}: Registered queue '{name}' with priority {priority.name}"
        )

    def _get_available_workers(self) -> list[int]:
        """
        Get indices of available workers.

        Returns:
            List of indices of available workers
        """
        available = []
        for i, worker in enumerate(self.workers):
            if hasattr(worker, "status") and worker.status.name == "READY":
                available.append(i)
        return available[:self._max_available_workers]

    def _get_queue_sizes(self) -> dict[str, int]:
        """
        Get sizes of all queues.

        Returns:
            Dictionary mapping queue names to their sizes
        """
        return {name: config.queue.qsize() for name, config in self.queues.items()}

    def _calculate_worker_distribution(self) -> dict[str, int]:
        """
        Calculate worker distribution among queues based on priorities and queue sizes.

        Returns:
            Dictionary mapping queue names to number of workers to assign
        """
        queue_sizes = self._get_queue_sizes()
        available_workers_count = len(self._get_available_workers())

        if available_workers_count == 0:
            return {}

        non_empty_queues = {
            name: size for name, size in queue_sizes.items() if size > 0
        }

        if not non_empty_queues:
            return {}

        sorted_queues = sorted(
            non_empty_queues.items(),
            key=lambda x: self.queues[x[0]].priority.value
        )

        distribution = {}
        remaining_workers = available_workers_count

        for queue_name, _ in sorted_queues:
            if remaining_workers <= 0:
                break
                
            config = self.queues[queue_name]
            alloc = min(config.min_workers, remaining_workers)
            if config.max_workers is not None:
                alloc = min(alloc, config.max_workers)
                
            if alloc > 0:
                distribution[queue_name] = alloc
                remaining_workers -= alloc

        if remaining_workers > 0:
            priority_groups = {
                QueuePriority.HIGH: [],
                QueuePriority.MEDIUM: [],
                QueuePriority.LOW: [],
            }
            
            for queue_name, _ in sorted_queues:
                priority = self.queues[queue_name].priority
                priority_groups[priority].append(queue_name)

            for priority in [QueuePriority.HIGH, QueuePriority.MEDIUM, QueuePriority.LOW]:
                if not priority_groups[priority] or remaining_workers <= 0:
                    continue
                    
                weight = 1 / (priority.value * 0.5)
                workers_for_group = min(
                    int(remaining_workers * weight),
                    remaining_workers
                )
                
                if workers_for_group <= 0:
                    continue
                    
                workers_per_queue = workers_for_group // len(priority_groups[priority])
                remainder = workers_for_group % len(priority_groups[priority])
                
                for i, queue_name in enumerate(priority_groups[priority]):
                    current = distribution.get(queue_name, 0)
                    config = self.queues[queue_name]
                    
                    available_slot = max(0, config.max_workers - current) if config.max_workers else float('inf')
                    
                    to_add = workers_per_queue + (1 if i < remainder else 0)
                    to_add = min(to_add, available_slot, remaining_workers)
                    
                    if to_add <= 0:
                        continue
                        
                    distribution[queue_name] = distribution.get(queue_name, 0) + to_add
                    remaining_workers -= to_add
                    
                    if remaining_workers <= 0:
                        break
                if remaining_workers <= 0:
                    break

        return distribution

    async def _assign_worker_to_queue(self, worker_idx: int, queue_name: str) -> None:
        """
        Assign a worker to process tasks from a specific queue.

        Args:
            worker_idx (int): Index of the worker to assign
            queue_name (str): Name of the queue to assign the worker to
        """
        worker = self.workers[worker_idx]
        config = self.queues[queue_name]

        try:
            if config.queue.qsize() > 0:
                task_data = await config.queue.get()
                self.worker_assignments[worker_idx] = queue_name

                await config.handler(worker, task_data)

                config.queue.task_done()

        except Exception as e:
            logger.error(
                f"Error assigning worker {worker_idx} to queue {queue_name}: {e}"
            )
        finally:
            self.worker_assignments[worker_idx] = None

    async def _monitor_and_distribute(self) -> None:
        """Main monitoring and distribution loop."""
        while self._running:
            try:
                available_workers = self._get_available_workers()

                if not available_workers:
                    logger.debug(
                        f"No available workers. Total workers: {len(self.workers)}"
                    )
                    await asyncio.sleep(self.check_interval)
                    continue
                distribution = self._calculate_worker_distribution()

                if not distribution:
                    logger.debug("All queues are empty, waiting for new tasks...")
                    await asyncio.sleep(self.check_interval * 10)
                    continue

                tasks = []
                worker_idx = 0

                for queue_name, worker_count in distribution.items():
                    for _ in range(
                        min(worker_count, len(available_workers) - worker_idx)
                    ):
                        if worker_idx < len(available_workers):
                            tasks.append(
                                self._assign_worker_to_queue(
                                    available_workers[worker_idx], queue_name
                                )
                            )
                            worker_idx += 1

                if tasks:
                    await asyncio.gather(*tasks, return_exceptions=True)

            except Exception as e:
                logger.error(f"Error in monitor_and_distribute: {e}")

            await asyncio.sleep(self.check_interval)

    async def start(self) -> None:
        """Start monitoring the queues."""
        if self._running:
            logger.warning(f"{__class__.__name__} is already running")
            return

        self._running = True
        self._monitor_task = asyncio.create_task(self._monitor_and_distribute())
        logger.info(f"{__class__.__name__} started")

    async def stop(self) -> None:
        """Stop monitoring the queues."""
        if not self._running:
            return

        self._running = False

        if self._monitor_task:
            self._monitor_task.cancel()
            try:
                await self._monitor_task
            except asyncio.CancelledError:
                pass

        logger.info("PriorityQueueManager stopped")

    def get_status(self) -> dict[str, Any]:
        """
        Get current manager status.

        Returns:
            Dictionary containing:
                - running: Whether manager is running
                - queues: Current queue sizes
                - available_workers: Number of available workers
                - total_workers: Total number of workers
                - worker_assignments: Current worker assignments
        """
        return {
            "running": self._running,
            "queues": self._get_queue_sizes(),
            "available_workers": len(self._get_available_workers()),
            "total_workers": len(self.workers),
            "worker_assignments": {
                idx: assignment
                for idx, assignment in self.worker_assignments.items()
                if assignment is not None
            },
        }

    def limit_available_workers(self, limit: int) -> None:
        """
        Limit the number of available workers.

        Args:
            limit (int): Maximum number of workers to make available
        """
        self._max_available_workers = max(1, limit)
        
    def reset_worker_limit(self) -> None:
        """Reset worker limit to total number of workers."""
        self._max_available_workers = len(self.workers)