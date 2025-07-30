import asyncio

from app.infrastructure.db.crud import *
from app.core import logger, settings
from ..managers import *
from .worker import *


class GlobalTitlesUpdater:
    def __init__(self) -> None:
        self._proxy_manager = ProxyManager()
        self._task_manager = TaskManager()

        self._queue: asyncio.Queue = asyncio.Queue()

        # Workers
        self._workers: list[FullParserWorker] = []

        # Tasks
        self._worker_scaler_task: asyncio.Task | None = None
        self._idle_task: asyncio.Task | None = None
        self._worker_manager_task: asyncio.Task | None = None

        self._running = False

        # Supported providers
        self._providers = [SourceProvider.MAL, SourceProvider.REMANGA]

    async def initialize(self) -> None:
        """Initialize the GlobalTitlesUpdater by setting up managers and queues."""

        # Initialize managers
        await self._proxy_manager.initialize()
        await self._task_manager.initialize()

        # Fetch and validate values
        await self._proxy_manager.fetch_and_store_values()
        await self._proxy_manager.validate_values()

        # Determine optimal number of workers
        num_workers = await self._calculate_optimal_workers()

        # Create workers
        self._workers = [
            FullParserWorker(i, self._proxy_manager, self._task_manager)
            for i in range(num_workers)
        ]

        logger.info(f"{self.__class__.__name__} initialized successfully.")

    async def _calculate_optimal_workers(self) -> int:
        """Calculate optimal number of workers based on available proxies."""
        proxy_stats = await self._proxy_manager.get_stats()
        active_proxies = proxy_stats.get("active_values", 0)

        if active_proxies == 0:
            logger.debug("No active proxies found, using 2 worker")
            return 2

        # Use conservative approach: 2 worker per +-2 proxies to avoid rate limiting
        optimal_workers = max(2, min(active_proxies // 2, 20))
        logger.debug(
            f"Calculated {optimal_workers} workers for {active_proxies} proxies"
        )

        return optimal_workers

    async def _adjust_workers_count(self) -> None:
        """Adjust the number of active workers based on available proxies."""
        if self._queue.empty():
            return

        optimal_workers = await self._calculate_optimal_workers()
        current_active = len(
            [w for w in self._workers if w.status != WorkerStatus.DISABLED]
        )

        # Scale down workers
        if optimal_workers < current_active:
            workers_to_stop = current_active - optimal_workers
            stopped_count = 0
            for worker in self._workers:
                if stopped_count >= workers_to_stop:
                    break
                if worker.status == WorkerStatus.READY:
                    worker.status = WorkerStatus.DISABLED
                    stopped_count += 1
                    logger.info(
                        f"Worker {worker.id} temporarily disabled due to insufficient proxies"
                    )
        # Scale up workers
        elif optimal_workers > current_active:
            workers_to_start = optimal_workers - current_active
            started_count = 0

            # Try to enable disabled workers first
            for worker in self._workers:
                if started_count >= workers_to_start:
                    break

                if worker.status == WorkerStatus.DISABLED:
                    worker.status = WorkerStatus.READY
                    started_count += 1
                    logger.info(f"Worker {worker.id} reactivated")

            # If still need more workers, create new ones
            if (
                started_count < workers_to_start
                and len(self._workers) < optimal_workers
            ):
                new_workers_needed = min(
                    workers_to_start - started_count,
                    optimal_workers - len(self._workers),
                )

                for _ in range(new_workers_needed):
                    worker_id = len(self._workers)
                    self._workers.append(
                        FullParserWorker(
                            worker_id, self._proxy_manager, self._task_manager
                        )
                    )
                    logger.info(f"Created new worker {worker_id}")

    async def _worker_scaler(self) -> None:
        """Periodically check and adjust worker count based on proxy availability."""
        while self._running:
            await asyncio.sleep(60)
            try:
                await self._adjust_workers_count()
            except Exception as e:
                logger.error(f"{self.__class__.__name__}: Error in worker scaler: {e}")

    async def _load_parsing_queues(self) -> None:
        """Load pages that need to be parsed into queues."""
        for provider in self._providers:
            try:
                await self._load_provider_queue(provider)
            except Exception as e:
                logger.error(f"Failed to load queue for {provider.name}: {e}")

    async def _load_provider_queue(self, provider: SourceProvider) -> None:
        """Load pages for a specific provider into its queue."""
        # Get the total number of pages available
        total_pages = await self._get_total_pages(provider)
        if not total_pages:
            logger.warning(f"Could not determine total pages for {provider.name}")
            return

        # Get completed pages within the time frame
        completed_pages = set(
            await self._task_manager.get_completed_pages(provider),
        )

        # Calculate pages that need to be parsed
        all_pages = set(range(1, total_pages + 1))
        pages_to_parse = list(all_pages - completed_pages)

        # Add pages to queue
        for page in pages_to_parse:
            await self._queue.put((provider, page))

    async def _get_total_pages(self, provider: SourceProvider) -> int | None:
        """Get total number of pages for a provider."""
        try:
            proxy = await self._proxy_manager.get_value()

            if provider == SourceProvider.MAL:
                async with MalProvider() as client:
                    page_data = await client.get_page(page=1, proxy=proxy)
                    return page_data.pagination.last_visible_page

            elif provider == SourceProvider.REMANGA:
                # Remanga doesn't have clear pagination, use a conservative estimate
                # or implement a method to determine the last page
                return 1900  # Remanga has around 1900 pages * 30 = 57000 titles

        except Exception as e:
            logger.error(f"Failed to get total pages for {provider.name}: {e}")
            return None

    async def _worker_manager(self) -> None:
        """Manage workers and assign tasks from the queue."""
        while self._running:
            try:
                if self._queue.empty():
                    await asyncio.sleep(10)
                    continue

                # Find available workers and assign tasks
                for worker in self._workers:
                    if worker.status == WorkerStatus.READY and not self._queue.empty():
                        try:
                            provider, page = await self._queue.get()
                            asyncio.create_task(
                                self._process_worker_task(worker, provider, page)
                            )
                        except asyncio.QueueEmpty:
                            break

                await asyncio.sleep(1)

            except Exception as e:
                logger.error(f"{self.__class__.__name__}: Error in worker manager: {e}")
                await asyncio.sleep(1)

    async def _process_worker_task(
        self,
        worker: FullParserWorker,
        provider: SourceProvider,
        page: int,
    ) -> None:
        """Process a single worker task with error handling."""
        try:
            logger.info(
                f"Worker {worker.id} processing page {page} for {provider.name}"
            )
            await worker.process_page(provider, page)
        except WorkerError as e:
            # Return task to queue if it should be retried
            if e.should_retry:
                await self._queue.put((provider, page))
                logger.info(
                    f"Worker {worker.id}: Page {page} returned to queue for retry"
                )
        finally:
            self._queue.task_done()

    async def _update_cycle(self) -> None:
        """Run an idle cycle that periodically updates the queues."""
        while True:
            try:
                await asyncio.sleep(settings.GTP_UPDATE_INTERVAL.total_seconds())

                logger.info(f"{self.__class__.__name__}: Running update queue cycle...")

                # Update queues
                await self._load_parsing_queues()

                logger.info(f"{self.__class__.__name__}: Update queue cycle completed.")
            except Exception as e:
                logger.error(f"{self.__class__.__name__}: Error in idle cycle: {e}")

    async def start_parsing(self) -> None:
        """Start the parsing process."""
        if self._idle_task is not None:
            logger.warning(
                f"{self.__class__.__name__}: parsing cycle is already running."
            )
            return

        self._running = True

        # Load initial parsing queues
        await self._load_parsing_queues()

        self._idle_task = asyncio.create_task(self._update_cycle())
        self._worker_manager_task = asyncio.create_task(self._worker_manager())
        self._worker_scaler_task = asyncio.create_task(self._worker_scaler())
        logger.info(f"{self.__class__.__name__}: parsing cycle started.")

        try:
            await asyncio.gather(
                self._idle_task,
                self._worker_manager_task,
                self._worker_scaler_task,
            )
        except asyncio.CancelledError:
            logger.info(f"{self.__class__.__name__}: parsing cycle was cancelled.")

        logger.info(f"{self.__class__.__name__}: parsing cycle stopped.")

    async def stop(self) -> None:
        """Stop the GlobalTitlesUpdater and clean up resources."""
        self._running = False

        tasks_to_cancel = [
            self._idle_task,
            self._worker_manager_task,
            self._worker_scaler_task,
        ]

        for task in tasks_to_cancel:
            if task:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass

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
