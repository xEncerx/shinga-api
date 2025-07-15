from aiohttp.client_exceptions import ClientResponseError
from enum import Enum, auto

from app.domain.services.translation import Translator
from app.infrastructure.storage import MediaManger
from app.infrastructure.db.models import *
from app.infrastructure.managers import *
from app.infrastructure.db.crud import *
from app.core import logger, Language
from app.providers import *


class UpdWorkerStatus(Enum):
    """Enumeration representing the status of a worker."""

    READY = auto()
    WORKING = auto()
    ERROR = auto()


class UpdateWorkerError(Exception):
    """Custom exception for worker errors."""

    def __init__(
        self,
        title_id: str,
        message: str,
        status_code: int = 500,
        should_retry: bool = True,
    ):
        """
        Initialize the WorkerError with a status code and message.

        Args:
            title_id (str): ID of the title that failed to process.
            status_code (int): HTTP status code representing the error.
            message (str): Description of the error.
            should_retry (bool): Whether the task should be retried.
        """
        self.title_id = title_id
        self.status_code = status_code
        self.message = message
        self.should_retry = should_retry
        super().__init__(f"Error {status_code}: {message}")


class UpdateWorker:
    def __init__(
        self,
        worker_id: int,
        proxy_manager: ProxyManager,
        api_key_manager: ApiKeyManager,
    ) -> None:
        self.id = worker_id
        self.status = UpdWorkerStatus.READY

        # Initialize title providers
        self._remanga_client = RemangaProvider()
        self._shiki_client = ShikiProvider()
        self._mal_client = MalProvider()

        # Initialize utils
        self._cover_manager = MediaManger()
        self._translator = Translator()

        self._proxy_manager = proxy_manager
        self._api_key_manager = api_key_manager

    async def process_title(self, title_id: str) -> None:
        """Process a single title update task."""
        self.status = UpdWorkerStatus.WORKING

        try:
            proxy = await self._proxy_manager.get_value()
            if not proxy:
                raise UpdateWorkerError(
                    title_id, "No available proxies for the worker."
                )

            title: Title | None = await TitleCRUD.read.by_id(title_id) # type: ignore
            if not title:
                raise UpdateWorkerError(
                    title_id,
                    f"Title with ID {title_id} not found.",
                    status_code=404,
                    should_retry=False,
                )
            if title.extra_data.get("is_404", False):
                return  # Skip titles marked as 404

            try:
                match title.source_provider:
                    case SourceProvider.REMANGA:
                        new_title = await self._remanga_client.get_by_id(title.source_id)
                    case SourceProvider.SHIKIMORI:
                        new_title = await self._shiki_client.get_by_id(
                            title.source_id, proxy=proxy
                        )
                    case SourceProvider.MAL:
                        new_title = await self._mal_client.get_by_id(
                            title.source_id, proxy=proxy
                        )
                    case SourceProvider.CUSTOM:
                        new_title = None  # Custom titles processing not implemented yet
                    case _:
                        raise UpdateWorkerError(
                            title_id,
                            f"Unknown source provider: {title.source_provider}",
                            should_retry=False,
                        )
            except ClientResponseError as e:
                if e.status == 404:
                    # Set title as 404 if not found, to dont process it again later
                    logger.warning(
                        f"Title with ID {title.id} not found in {title.source_provider.name}. Marking as 404."
                    )
                    title.extra_data["is_404"] = True
                    await TitleCRUD.update.fields(
                        title_id,
                        extra_data=title.extra_data,
                    )
                    return
                new_title = None  # Handle other client errors gracefully

            if not new_title:
                raise UpdateWorkerError(
                    title_id,
                    f"Title with ID {title.id} cant be parse from {title.source_provider.name}.",
                    status_code=400,
                )

            # Update title fields with new data
            title.name_ru = new_title.name_ru or title.name_ru
            title.name_en = new_title.name_en or title.name_en
            title.alt_names = new_title.alt_names
            title.chapters = new_title.chapters or title.chapters
            title.volumes = new_title.volumes or title.volumes
            title.views = new_title.views or title.views
            title.status = new_title.status
            title.date = new_title.date
            title.rating = new_title.rating or title.rating
            title.scored_by = new_title.scored_by or title.scored_by
            title.popularity = new_title.popularity or title.popularity
            title.favorites = new_title.favorites or title.favorites
            title.description = TitleDescription(
                en=new_title.description.en or title.description.en,
                ru=new_title.description.ru or title.description.ru,
            )
            title.genres = new_title.genres or title.genres
            title.updated_at = new_title.updated_at

            # api_key = await self._api_key_manager.get_value()
            # if api_key:
            #     await self._translate_title(
            #         title,
            #         api_key=api_key,
            #         proxy=proxy,
            #     )
            #     await asyncio.sleep(8)  # Rate limit for translation API

            result = await TitleCRUD.create.upsert(title)
            if not result:
                raise UpdateWorkerError(
                    title.id, f"Failed to update title {title.id} in the database."
                )

            logger.info(f"Worker {self.id}: Successfully processed title {title_id}")

        except UpdateWorkerError as e:
            raise  # Re-raise UpdateWorkerError as is
        except Exception as e:
            logger.error(
                f"Worker {self.id}: Unexpected error processing title {title_id}: {e}"
            )
            raise UpdateWorkerError(title_id, f"Unexpected error: {str(e)}")
        finally:
            self.status = UpdWorkerStatus.READY

    async def _translate_title(self, title: Title, api_key: str, proxy: str) -> None:
        if title.description.en and not title.description.ru:
            # Translate English description to Russian
            translation_data = {
                "description": title.description.en,
            }
            if title.name_en and not title.name_ru:
                translation_data["title"] = title.name_en

            data = await self._translator.translate(
                text=translation_data,
                target_lang=Language.RU,
                openai_api_key=api_key,
                proxy=proxy,
            )

            if not data:
                return

            if "description" in data:
                title.description = TitleDescription(
                    en=title.description.en,
                    ru=data["description"],
                )
            if "title" in data and not title.name_ru:
                title.name_ru = data["title"]
        elif title.description.ru and not title.description.en:
            # Translate Russian description to English
            translation_data = {
                "description": title.description.ru,
            }
            if title.name_ru and not title.name_en:
                translation_data["title"] = title.name_ru

            data = await self._translator.translate(
                text=translation_data,
                target_lang=Language.EN,
                openai_api_key=api_key,
                proxy=proxy,
            )

            if not data:
                return

            if "description" in data:
                title.description = TitleDescription(
                    en=data["description"],
                    ru=title.description.ru,
                )
            if "title" in data and not title.name_en:
                title.name_en = data["title"]

    async def cleanup(self) -> None:
        """Cleanup resources used by the worker."""
        # Close all http clients and managers
        await self._remanga_client.close()
        await self._shiki_client.close()
        await self._mal_client.close()
        await self._cover_manager.close()
        await self._translator.close()
