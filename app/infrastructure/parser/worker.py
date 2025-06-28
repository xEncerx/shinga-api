from enum import Enum, auto

from app.infrastructure.storage import CoverManger
from app.domain.services.translation import Translator
from app.providers import MalProvider
from app.core import logger


class WorkerStatus(Enum):
    READY = auto()
    WORKING = auto()
    ERROR = auto()


class WorkerError(Exception):
    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        self.message = message
        super().__init__(f"Error {status_code}: {message}")


class Worker:
    def __init__(self, worker_id: int) -> None:
        self.worker_id = worker_id
        self.status = WorkerStatus.READY
        self.current_task = None

        self._mal_client = MalProvider()
        self._translator = Translator()
        self._cover_manager = CoverManger()

    async def parse(self, value: int, proxy: str, api_key: str) -> None:
        self.status = WorkerStatus.WORKING
        self.current_task = value

        # Parse title
        data = await self._mal_client.get_by_id(
            value,
            proxy=proxy
        )
        if isinstance(data, int) or data is None:
            self.status = WorkerStatus.ERROR
            raise WorkerError(data or 400, f"Failed to process task: {value}")
        
        # Save covers
        new_urls = await self._cover_manager.batch_save(
            [
                (data.cover.url, "mal", str(data.id), ""),
                (data.cover.large_url, "mal", str(data.id), "l"),
                (data.cover.small_url, "mal", str(data.id), "s"),
            ],
            proxy=proxy,
        )
        data.cover.url = new_urls[0] or data.cover.url
        data.cover.large_url = new_urls[1] or data.cover.large_url
        data.cover.small_url = new_urls[2] or data.cover.small_url

        self.status = WorkerStatus.READY
        self.current_task = None
        logger.success(f"Worker id_{self.worker_id} successfully processed task: {value}")

    async def cleanup(self) -> None:
        """Cleanup resources used by the worker."""
        await self._mal_client.close()
        await self._translator.close()
        await self._cover_manager.close()
