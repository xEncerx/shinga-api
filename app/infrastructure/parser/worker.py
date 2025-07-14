from enum import Enum, auto
from itertools import chain
import asyncio

from app.domain.services.translation import Translator
from app.infrastructure.managers import ProxyManager
from app.infrastructure.storage import MediaManger
from app.infrastructure.db.models import *
from app.infrastructure.db.crud import *
from app.providers import MalProvider
from app.utils import TaskTracker
from app.core import logger


class WorkerStatus(Enum):
    """Enumeration representing the status of a worker."""

    READY = auto()
    WORKING = auto()
    ERROR = auto()


class WorkerError(Exception):
    """Custom exception for worker errors."""

    def __init__(self, status_code: int, message: str):
        """
        Initialize the WorkerError with a status code and message.

        Args:
            status_code (int): HTTP status code representing the error.
            message (str): Description of the error.
        """
        self.status_code = status_code
        self.message = message
        super().__init__(f"Error {status_code}: {message}")


class WorkerAction(Enum):
    """Enumeration representing the actions a worker can perform."""

    PARSING = auto()
    TRANSLATE = auto()
    UPDATE = auto()


class Worker:
    """Worker class for handling tasks related to parsing, translating, and updating titles."""

    def __init__(self, worker_id: int, proxy_manager: ProxyManager) -> None:
        """
        Initialize the Worker instance.

        Args:
            worker_id (int): Unique identifier for the worker.
            proxy_manager (ProxyManager): Instance of ProxyManager to manage proxies.
        """
        self.worker_id = worker_id
        self.status = WorkerStatus.READY

        self._proxy_manager = proxy_manager
        self._mal_client = MalProvider()
        self._translator = Translator()
        self._cover_manager = MediaManger()

    async def parsing(self, value: int) -> None:
        """
        Parse a page of titles from MyAnimeList and save their covers.

        Args:
            value (int): Page number to parse titles from.
        """
        self.status = WorkerStatus.WORKING

        # Get proxy from the proxy manager
        proxy = await self._proxy_manager.get_value()
        if not proxy:
            self.status = WorkerStatus.ERROR
            raise WorkerError(401, "No available proxy for task")

        # Parse page of titles
        page = await self._mal_client.get_page(page=value, proxy=proxy)

        if not page.data:
            self.status = WorkerStatus.ERROR
            raise WorkerError(101, f"Cant parse data from page: {value}")

        # Save covers for titles in batches
        batch_size = 10
        batches = [
            page.data[i : i + batch_size] for i in range(0, len(page.data), batch_size)
        ]
        for batch in batches:
            images_data = await self._cover_manager.batch_covers_save(
                images=[
                    (title.cover.large_url, "mal", str(title.source_id))
                    for title in batch
                ],
                proxy=proxy,
            )
            # Update titles with new cover URLs
            for title, covers in zip(batch, images_data):
                title.cover = TitleCover(
                    url=covers[0],
                    small_url=covers[1],
                    large_url=covers[2],
                )

            await asyncio.sleep(0.1)
            proxy = await self._proxy_manager.get_value()

        # Save titles to database
        result = await TitleCRUD.create.bulk(list(chain(*batches)))
        if not result:
            self.status = WorkerStatus.ERROR
            raise WorkerError(101, f"Failed to save titles from page: {value}")

        # Mark tasks as done in TaskTracker
        await TaskTracker.mark_done(value, "global_mal_parser_tasks")

        # Finish processing and reset worker status
        self.status = WorkerStatus.READY
        logger.success(
            f"Worker id_{self.worker_id} successfully processed task(parsing): {value}"
        )

    async def translate(self, value: str, api_key: str) -> None:
        """
        Translate the title and description of a title by its ID.

        Args:
            value (int): The ID of the title to translate.
            api_key (str): The OpenAI API key to use for translation.
        """
        self.status = WorkerStatus.WORKING

        # Get title by ID
        title = await TitleCRUD.read.by_id(value)
        if not title:
            self.status = WorkerStatus.ERROR
            raise WorkerError(204, f"Title not found: {value}")

        # Get proxy
        proxy = await self._proxy_manager.get_value()
        if not proxy:
            self.status = WorkerStatus.ERROR
            raise WorkerError(401, "No available proxy for task")

        # Translate data
        translated_data = await self._translator.translate(
            {
                "title": title.name_en,  # type: ignore
                "description": title.description.en or "",
            },
            proxy=proxy,
            openai_api_key=api_key,
        )
        if not translated_data:
            self.status = WorkerStatus.ERROR
            raise WorkerError(201, f"Failed to translate title: {value}")

        # Update title with translated data
        title.name_ru = translated_data.get("title")
        title.description = TitleDescription(
            en=title.description.en,
            ru=translated_data.get("description"),
        )
        result = await TitleCRUD.create.upsert(title)
        if not result:
            self.status = WorkerStatus.ERROR
            raise WorkerError(201, f"Failed to update title(translation): {value}")

        # Finish processing and reset worker status
        self.status = WorkerStatus.READY
        logger.success(
            f"Worker id_{self.worker_id} successfully processed task(translate): {value}"
        )

    async def update_data(self, value: str) -> None:
        """
        Update the title data by its ID.

        Args:
            value (int): The ID of the title to update.
        """
        self.status = WorkerStatus.WORKING

        # Get title by ID
        title = await TitleCRUD.read.by_id(value)
        if not title:
            self.status = WorkerStatus.ERROR
            raise WorkerError(304, f"Title not found: {value}")

        if title.source_provider != SourceProvider.MAL:
            raise WorkerError(
                306,
                f"Provider: {title.source_provider.name} is not supported for update",
            )

        # Get proxy
        proxy = await self._proxy_manager.get_value()
        if not proxy:
            self.status = WorkerStatus.ERROR
            raise WorkerError(401, "No available proxy for task")

        if not title.source_id:
            self.status = WorkerStatus.ERROR
            raise WorkerError(304, f"Title source_id not found: {value}")

        # Parse title
        data = await self._mal_client.get_by_id(int(title.source_id), proxy=proxy)
        if data is None:
            self.status = WorkerStatus.ERROR
            raise WorkerError(301, f"Failed to process task: {value}")

        title.chapters = data.chapters
        title.volumes = data.volumes
        title.views = data.views
        title.status = data.status
        title.date = data.date
        title.rating = data.rating
        title.scored_by = data.scored_by
        title.popularity = data.popularity
        title.favorites = data.favorites

        result = await TitleCRUD.create.upsert(title)

        if not result:
            self.status = WorkerStatus.ERROR
            raise WorkerError(301, f"Failed to update title: {value}")

        # Finish processing and reset worker status
        self.status = WorkerStatus.READY
        logger.success(
            f"Worker id_{self.worker_id} successfully processed task(updating): {value}"
        )

    async def cleanup(self) -> None:
        """Cleanup resources used by the worker."""
        await self._mal_client.close()
        await self._translator.close()
        await self._cover_manager.close()
