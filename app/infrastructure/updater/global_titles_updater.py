import asyncio

from app.infrastructure.db.crud import *
from app.infrastructure.parser import *
from app.core import logger, settings
from ..managers import *
from .worker import *


class GlobalTitlesUpdater:
    def __init__(self, num_workers: int = 1) -> None:
        self._api_key_manager = ApiKeyManager()
        self._proxy_manager = ProxyManager()

        self._update_queue = asyncio.Queue()

        self._workers = [
            UpdateWorker(i, self._proxy_manager, self._api_key_manager)
            for i in range(num_workers)
        ]

        self._num_workers = num_workers
        self._idle_task: asyncio.Task | None = None
        self._worker_manager_task: asyncio.Task | None = None
        self._running = False

    async def load_update_queue(self) -> None:
        """Load titles into the update queue that need updating."""
        titles = await TitleCRUD.read.for_update(
            time_ago=settings.GTP_UPDATE_INTERVAL,
        )

        self._clear_queue(self._update_queue)

        for title_id in titles:
            await self._update_queue.put(title_id)

        logger.info(f"Loaded {len(titles)} titles into the update queue.")

    async def _worker_manager(self) -> None:
        """Manage workers and assign tasks from the queue."""
        while self._running:
            try:
                if self._update_queue.empty():
                    await asyncio.sleep(1)
                    continue

                # Find available workers and assign tasks
                for worker in self._workers:
                    if (
                        worker.status == UpdWorkerStatus.READY
                        and not self._update_queue.empty()
                    ):
                        try:
                            title_id = await self._update_queue.get()
                            asyncio.create_task(
                                self._process_worker_task(worker, title_id)
                            )
                        except asyncio.QueueEmpty:
                            break

                await asyncio.sleep(0.1)

            except Exception as e:
                logger.error(f"{self.__class__.__name__}: Error in worker manager: {e}")
                await asyncio.sleep(1)

    async def _process_worker_task(self, worker: UpdateWorker, title_id: str) -> None:
        """Process a single worker task with error handling."""
        try:
            await worker.process_title(title_id)
            logger.debug(f"Worker {worker.id}: Task completed for title {title_id}")
        except UpdateWorkerError as e:
            # Return task to queue if it should be retried
            if e.should_retry:
                await asyncio.sleep(10)
                await self._update_queue.put(e.title_id)
                logger.info(
                    f"Worker {worker.id}: Title {e.title_id} returned to queue for retry"
                )
        finally:
            self._update_queue.task_done()
            worker.status = UpdWorkerStatus.READY

    async def _update_cycle(self) -> None:
        """Run an idle cycle that periodically updates the queues."""
        while True:
            try:
                await asyncio.sleep(settings.QUEUE_UPDATE_INTERVAL)

                logger.info(f"{self.__class__.__name__}: Running update queue cycle...")

                # Update queues
                await self.load_update_queue()

                logger.info(f"{self.__class__.__name__}: Update queue cycle completed.")
            except Exception as e:
                logger.error(f"{self.__class__.__name__}: Error in idle cycle: {e}")

    async def idle(self) -> None:
        """Start an idle cycle that periodically updates the queues."""
        if self._idle_task is not None:
            logger.warning(f"{self.__class__.__name__}: idle cycle is already running.")
            return

        self._running = True

        self._idle_task = asyncio.create_task(self._update_cycle())
        self._worker_manager_task = asyncio.create_task(self._worker_manager())
        logger.info(f"{self.__class__.__name__}: idle cycle started.")

        try:
            await asyncio.gather(self._idle_task, self._worker_manager_task)
        except asyncio.CancelledError:
            logger.info(f"{self.__class__.__name__}: idle cycle was cancelled.")

        logger.info(f"{self.__class__.__name__}: idle cycle stopped.")

    async def initialize(self) -> None:
        """Initialize the GlobalTitlesUpdater by setting up managers and queues."""

        # Initialize API key and proxy managers
        await self._api_key_manager.initialize()
        await self._proxy_manager.initialize()

        # Fetch and validate API keys and proxies
        await self._api_key_manager.fetch_and_store_values()
        await self._api_key_manager.validate_values()
        await self._proxy_manager.fetch_and_store_values()
        await self._proxy_manager.validate_values()

        # Load queues
        await self.load_update_queue()

        logger.info(f"{self.__class__.__name__} initialized successfully.")

    async def stop(self) -> None:
        """Stop the GlobalTitlesUpdater and clean up resources."""
        self._running = False

        if self._idle_task:
            self._idle_task.cancel()
            try:
                await self._idle_task
            except asyncio.CancelledError:
                pass

        if self._worker_manager_task:
            self._worker_manager_task.cancel()
            try:
                await self._worker_manager_task
            except asyncio.CancelledError:
                pass

        await self._api_key_manager.cleanup()
        await self._proxy_manager.cleanup()

        for worker in self._workers:
            await worker.cleanup()

        logger.info(f"{self.__class__.__name__} stopped")

    async def __aenter__(self) -> "GlobalTitlesUpdater":
        """Enter the context manager and initialize the parser."""
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit the context manager and clean up resources."""
        await self.stop()
        logger.info(f"{self.__class__.__name__} finished")

    @staticmethod
    def _clear_queue(queue: asyncio.Queue) -> None:
        """Clear the specified queue."""
        while not queue.empty():
            try:
                queue.get_nowait()
                queue.task_done()
            except:
                break
