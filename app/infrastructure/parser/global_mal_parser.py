from typing import Any
import asyncio

from app.infrastructure.db.crud import *
from app.infrastructure.parser import *
from app.providers import MalProvider
from app.core import logger, settings
from app.utils import TaskTracker
from ..managers import *


class GlobalMalParser:
    """GlobalMalParser is a class that manages the parsing, translation, and updating of titles from MyAnimeList (MAL)."""

    def __init__(self, num_workers: int = 2) -> None:
        """
        Initialize the GlobalMalParser with the specified number of workers.
        Args:
            num_workers (int): Number of worker instances to create.
        """
        self._api_key_manager = ApiKeyManager()
        self._proxy_manager = ProxyManager()

        self._parsing_queue = asyncio.Queue()
        self._translation_queue = asyncio.Queue()
        self._update_queue = asyncio.Queue()

        self.workers = [Worker(i, self._proxy_manager) for i in range(num_workers)]

        self._queue_manager = PriorityQueueManager(workers=self.workers)

        self._class = __class__.__name__
        self._num_workers = num_workers
        self._idle_task: asyncio.Task | None = None

    def _register_queues(
        self,
        max_translation_workers: int = 1,
    ) -> None:
        """Register queues with the queue manager."""
        self._queue_manager.register_queue(
            name="parsing_queue",
            queue=self._parsing_queue,
            priority=QueuePriority.HIGH,
            handler=self._handle_parsing_task,
        )
        self._queue_manager.register_queue(
            name="translation_queue",
            queue=self._translation_queue,
            priority=QueuePriority.MEDIUM,
            handler=self._handle_translation_task,
            max_workers=max_translation_workers,
        )
        self._queue_manager.register_queue(
            name="update_queue",
            queue=self._update_queue,
            priority=QueuePriority.MEDIUM,
            handler=self._handle_update_task,
        )

    async def _handle_parsing_task(self, worker: Worker, data: Any) -> None:
        """
        Parser task handler

        Args:
            worker (Worker): The worker instance handling the task.
            data (Any): The data to be parsed, typically a page number from MAL.
        """
        await self._try_unlimit_workers()

        try:
            await worker.parsing(data)
        except WorkerError as e:
            await self._handle_worker_error(worker, e, data, self._parsing_queue)
        except Exception as e:
            logger.error(
                f"Unexpected error in parsing worker id_{worker.worker_id}: {e}"
            )
            worker.status = WorkerStatus.ERROR

    async def _handle_translation_task(self, worker: Worker, data: Any) -> None:
        """
        Translation task handler

        Args:
            worker (Worker): The worker instance handling the task.
            data (Any): The data to be translated, typically a title ID.
        """
        await self._try_unlimit_workers()

        try:
            api_key = await self._api_key_manager.get_value()
            if not api_key:
                logger.debug("No available API key.")
                await self._translation_queue.put(data)
                await asyncio.sleep(5)
                return

            await worker.translate(data, api_key=api_key)
        except WorkerError as e:
            await self._handle_worker_error(worker, e, data, self._translation_queue)
        except Exception as e:
            logger.error(
                f"Unexpected error in translation worker id_{worker.worker_id}: {e}"
            )
            worker.status = WorkerStatus.ERROR

    async def _handle_update_task(self, worker: Worker, data: Any) -> None:
        """
        Update task handler

        Args:
            worker (Worker): The worker instance handling the task.
            data (Any): The data to be updated, typically a title ID.
        """
        await self._try_unlimit_workers()

        try:
            await worker.update_data(data)
        except WorkerError as e:
            await self._handle_worker_error(worker, e, data, self._update_queue)
        except Exception as e:
            logger.error(
                f"Unexpected error in update worker id_{worker.worker_id}: {e}"
            )
            worker.status = WorkerStatus.ERROR

    async def _handle_worker_error(
        self,
        worker: Worker,
        error: WorkerError,
        data: Any,
        queue: asyncio.Queue,
    ) -> None:
        """
        Error handler for worker tasks.

        Args:
            worker (Worker): The worker instance that encountered the error.
            error (WorkerError): The error that occurred during the worker's task.
            data (Any): The data that was being processed when the error occurred.
            queue (asyncio.Queue): The queue to re-add the data for retrying.
        """
        # 1xx - parsing errors
        # 2xx - translation errors
        # 3xx - update errors
        # 4xx - Other errors

        logger.error(
            f"Worker id_{worker.worker_id} encountered an error: {error.message} (Status Code: {error.status_code})"
        )

        if error.status_code in [101, 201, 301]:
            logger.warning(
                f"Error in  Worker id_{worker.worker_id}: {error.message}. Retrying later."
            )
            await queue.put(data)
        elif error.status_code == 401:
            logger.debug(
                f"Worker id_{worker.worker_id} has no available proxy for task."
            )
            self._queue_manager.limit_available_workers(1)
            await asyncio.sleep(5)  # Wait before retrying
            await queue.put(data)

        worker.status = WorkerStatus.READY

    async def _try_unlimit_workers(self) -> None:
        """Reset worker limit if too many active proxies"""
        if self._queue_manager.max_available_workers != self._num_workers:
            proxy_stats_data = await self._proxy_manager.get_stats()
            if proxy_stats_data["active_values"] > 5:
                logger.info(f"Resetting worker limit.")
                self._queue_manager.reset_worker_limit()

    async def load_parsing_queue(self) -> None:
        """Load pages into the parsing queue based on the last processed ID."""
        self._clear_queue(self._parsing_queue)

        async with MalProvider() as mal:
            last_page = (
                await mal.get_page(
                    page=1,
                    proxy=await self._proxy_manager.get_value(),
                )
            ).pagination.last_visible_page

        tasks = await TaskTracker.get_missing_tasks(
            range(1, last_page + 1),
            table="global_mal_parser_tasks",
        )

        for page in tasks:
            await self._parsing_queue.put(page)

        logger.info(f"Loaded {len(tasks)} pages into the parsing queue.")

    async def load_translation_queue(self) -> None:
        """Load titles into the translation queue that need translation."""
        self._clear_queue(self._translation_queue)

        titles = []
        for title_id in titles:
            await self._translation_queue.put(title_id)

        logger.info(f"Loaded {len(titles)} titles into the translation queue.")

    async def load_update_queue(self) -> None:
        """Load titles into the update queue that need updating."""
        self._clear_queue(self._update_queue)

        titles = await TitleCRUD.read.for_update(
            time_ago=settings.GTP_UPDATE_INTERVAL,
        )
        for title_id in titles:
            await self._update_queue.put(title_id)

        logger.info(f"Loaded {len(titles)} titles into the update queue.")

    async def _update_cycle(self) -> None:
        """Run an idle cycle that periodically updates the queues."""
        while True:
            try:
                await asyncio.sleep(settings.QUEUE_UPDATE_INTERVAL)

                logger.info(f"{self._class}: Running update queue cycle...")

                # Update queues
                await self.load_parsing_queue()
                await self.load_update_queue()
                await self.load_translation_queue()

                logger.info(f"{self._class}: Update queue cycle completed.")
            except Exception as e:
                logger.error(f"{self._class}: Error in idle cycle: {e}")

    async def idle(self) -> None:
        """Start an idle cycle that periodically updates the queues."""
        if self._idle_task is not None:
            logger.warning(f"{self._class}: idle cycle is already running.")
            return

        self._idle_task = asyncio.create_task(self._update_cycle())
        logger.info(f"{self._class}: idle cycle started.")

        try:
            await self._idle_task
        except asyncio.CancelledError:
            logger.info(f"{self._class}: idle cycle was cancelled.")

        logger.info(f"{self._class}: idle cycle stopped.")

    def get_status(self) -> dict[str, Any]:
        """Get the current status of the GlobalMalParser."""
        queue_manager_status = self._queue_manager.get_status()

        return {
            "parser_class": self._class,
            "queue_manager": queue_manager_status,
            "workers_count": len(self.workers),
        }

    async def initialize(self) -> None:
        """Initialize the GlobalMalParser by setting up API keys, proxies, and queues."""
        # Initialize API key and proxy managers
        await self._api_key_manager.initialize()
        await self._proxy_manager.initialize()

        # Fetch and validate API keys and proxies
        await self._api_key_manager.fetch_and_store_values()
        await self._api_key_manager.validate_values()
        await self._proxy_manager.fetch_and_store_values()
        await self._proxy_manager.validate_values()

        # Get api_key_manager stats
        api_key_stats = await self._api_key_manager.get_stats()

        # Register queues with the queue manager
        self._register_queues(
            max_translation_workers=api_key_stats["total_values"],
        )

        # Load initial queues
        await self.load_parsing_queue()
        await self.load_translation_queue()
        await self.load_update_queue()

        # Start the queue manager
        await self._queue_manager.start()

        logger.info(f"{self._class} initialized successfully.")

    async def stop(self) -> None:
        """Clean up resources and close connections."""
        await self._queue_manager.stop()

        await self._api_key_manager.cleanup()
        await self._proxy_manager.cleanup()

        for worker in self.workers:
            await worker.cleanup()

        logger.info(f"{self._class} finished")

    async def __aenter__(self) -> "GlobalMalParser":
        """Enter the context manager and initialize the parser."""
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit the context manager and clean up resources."""
        await self.stop()
        logger.info(f"{self._class} finished")

    @staticmethod
    def _clear_queue(queue: asyncio.Queue) -> None:
        """Clear the specified queue."""
        while not queue.empty():
            try:
                queue.get_nowait()
                queue.task_done()
            except:
                break
