from time import perf_counter
import asyncio

from .value import ApiKeyManager, ProxyManager
from app.infrastructure.parser import *
from app.core import logger

class QueueManager:
    """
    A manager for distributing tasks among workers with proxy and API key management.
    
    Handles task queue initialization, worker coordination, and resource management
    for asynchronous parsing operations.
    """

    def __init__(self, num_workers: int = 2) -> None:
        """
        Initialize the QueueManager with specified number of workers.
        
        Args:
            num_workers: Number of worker instances to create (default: 2)
        """

        self._api_key_manager = ApiKeyManager()
        self._proxy_manager = ProxyManager()
        
        self.queue = asyncio.Queue()
        self.workers = [
            Worker(i) for i in range(num_workers)
        ]

    async def initialize(self) -> None:
        """
        Initialize all components and prepare for operation.
        
        Performs the following steps:
        1. Initializes API key and proxy managers
        2. Fetches and validates available resources
        3. Loads initial tasks into the queue
        """
        await self._api_key_manager.initialize()
        await self._proxy_manager.initialize()

        await self._api_key_manager.fetch_and_store_values()
        await self._api_key_manager.validate_values()
        await self._proxy_manager.fetch_and_store_values()
        await self._proxy_manager.validate_values()

        await self._load_queue()

        logger.success("QueueManager initialized successfully.")

    async def _load_queue(self) -> None:
        """
        Populate the task queue with initial work items.
        """
        for item in range(1, 100):
            await self.queue.put(item)

    async def _handle_worker_error(self, worker: Worker, error: WorkerError) -> None:
        """
        Handle errors occurring during worker execution.
        
        Args:
            worker: The worker instance that encountered the error
            error: The WorkerError containing status code and message
            
        Special handling for:
        - 429 (Rate Limit): Returns task to queue for retry
        - Other errors: Logs and resets worker status
        """
        logger.error(f"Worker {worker.worker_id} encountered an error: {error.message} (Status Code: {error.status_code})")

        if error.status_code == 429:
            logger.warning(f"Worker {worker.worker_id} is rate limited. Retrying later.")
            await self.queue.put(worker.current_task)

        worker.status = WorkerStatus.READY

    async def _assign_task(self, worker: Worker) -> None:
        """
        Assign a task to an available worker.
        
        Args:
            worker: Worker instance to assign task to
        """
        if not self.queue.empty() and worker.status == WorkerStatus.READY:
            data = await self.queue.get()
            try:
                proxy = await self._proxy_manager.get_value()
                # api_key = await self._api_key_manager.get_value()
                api_key = "2"
                if not proxy or not api_key:
                    logger.error("No available proxy or API key.")
                    await self.queue.put(data)
                    return
                
                data = await worker.parse(data, proxy=proxy, api_key=api_key)
            except WorkerError as e:
                await self._handle_worker_error(worker, e)
            except Exception as e:
                print(f"Unexpected error in worker {worker.worker_id}: {e}")
                worker.status = WorkerStatus.ERROR
            finally:
                self.queue.task_done()

    async def _monitor_workers(self) -> None:
        """
        Continuously monitor and assign tasks to available workers.
        
        Runs indefinitely until canceled during shutdown.
        """
        while True:
            tasks = []
            for worker in self.workers:
                if worker.status == WorkerStatus.READY:
                    tasks.append(self._assign_task(worker))
            
            if tasks:
                await asyncio.gather(*tasks)
            
            await asyncio.sleep(0.1)

    async def run(self) -> None:
        """
        Execute the main processing loop.
        """
        logger.info("Starting QueueManager...")
        start = perf_counter()
        monitor_task = asyncio.create_task(self._monitor_workers())

        await self.queue.join()

        monitor_task.cancel()
        try:
            await monitor_task
        except asyncio.CancelledError:
            pass
        
        await self._api_key_manager.cleanup()
        await self._proxy_manager.cleanup()

        logger.info(f"QueueManager finished in {perf_counter() - start:.2f} seconds.")
        logger.info("QueueManager finished")