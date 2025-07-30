from enum import Enum, auto
from tqdm import tqdm
import asyncio

# from app.domain.services.translation import Translator
from app.infrastructure.storage import MediaManger
from app.infrastructure.db.models import *
from app.infrastructure.managers import *
from app.infrastructure.db.crud import *
from app.providers import *
from app.core import logger


class WorkerStatus(Enum):
    """Enumeration representing the status of a worker."""

    READY = auto()
    WORKING = auto()
    DISABLED = auto()


class WorkerError(Exception):
    """Custom exception for worker errors."""

    def __init__(
        self,
        page: int,
        message: str,
        status_code: int = 500,
        should_retry: bool = True,
    ):
        """
        Initialize the WorkerError with a status code and message.

        Args:
            page (int): Page number or identifier related to the error.
            status_code (int): HTTP status code representing the error.
            message (str): Description of the error.
            should_retry (bool): Whether the task should be retried.
        """
        self.page = page
        self.status_code = status_code
        self.message = message
        self.should_retry = should_retry
        super().__init__(f"Error {status_code}: {message}")


class FullParserWorker:
    def __init__(
        self,
        worker_id: int,
        proxy_manager: ProxyManager,
        page_tracker: TaskManager,
    ) -> None:
        self.id = worker_id
        self.status = WorkerStatus.READY

        # Initialize title providers
        self._remanga_client = RemangaProvider()
        self._mal_client = MalProvider()

        # Initialize managers
        self._proxy_manager = proxy_manager
        self._task_manager = page_tracker
        self._media_manager = MediaManger()

    async def process_page(self, provider: SourceProvider, page: int) -> None:
        """Process a single page from the specified provider."""
        self.status = WorkerStatus.WORKING
        try:
            # Get proxy if available
            proxy = (
                await self._proxy_manager.get_value() if self._proxy_manager else None
            )

            match provider:
                case SourceProvider.REMANGA:
                    # Remanga is sensitive to proxies. But since it has no rate limits, we can do without them.
                    page_data = await self._remanga_client.get_page(page)
                case SourceProvider.MAL:
                    page_data = await self._mal_client.get_page(page=page, proxy=proxy)
                case _:
                    raise WorkerError(
                        page,
                        f"Unsupported provider: {provider.name}",
                        status_code=400,
                        should_retry=False,
                    )

            if not page_data.data:
                raise WorkerError(
                    page,
                    f"No data found for page {page} from {provider.name}",
                    status_code=404,
                    should_retry=False,
                )

            # Process each title on the page
            for title in tqdm(page_data.data, desc=f"Page [{page}]"):
                await self._process_title(title, proxy)

            # Mark page as completed
            await self._task_manager.mark_page_completed(provider, page)

            logger.success(
                f"Worker {self.id} completed page {page} for {provider.name}"
            )
        except WorkerError:
            raise
        except Exception as e:
            logger.error(f"Worker {self.id} failed to process page {page}: {e}")
            raise WorkerError(
                page,
                f"Failed to process page {page} from {provider.name}: {str(e)}",
                status_code=500,
            )
        finally:
            self.status = WorkerStatus.READY

    async def _process_title(self, title: Title, proxy: Optional[str]) -> None:
        """Process a single title - either update existing or create new."""
        # Check if title exists in database
        existing_title: Title | None = await TitleCRUD.read.by_id(title.id)  # type: ignore

        if existing_title:
            # Update existing title
            await self._update_existing_title(existing_title, title)
        else:
            # Create new title with covers
            logger.debug(f"Creating new title: {title.id}")

            # Get full title data for remanga if title don't exists
            if title.source_provider == SourceProvider.REMANGA:
                try:
                    full_title_data = await self._remanga_client.get_by_id(
                        title.source_id
                    )
                    if full_title_data:
                        title = full_title_data
                except Exception as e:
                    logger.error(
                        f"Failed to fetch full title data for {title.source_id}: {e}"
                    )
            await self._create_new_title(title, proxy)

        await asyncio.sleep(0.1)  # Small delay to avoid overload

    async def _update_existing_title(self, existing: Title, new: Title) -> None:
        """Update existing title while preserving important fields."""
        result = await TitleCRUD.update.fields(
            title_id=existing.id,
            name_ru=new.name_ru or existing.name_ru,
            name_en=new.name_en or existing.name_en,
            alt_names=new.alt_names,
            chapters=new.chapters or existing.chapters,
            volumes=new.volumes or existing.volumes,
            views=new.views or existing.views,
            status=new.status,
            date=new.date,
            rating=new.rating or existing.rating,
            scored_by=new.scored_by or existing.scored_by,
            popularity=new.popularity or existing.popularity,
            favorites=new.favorites or existing.favorites,
            description=TitleDescription(
                en=new.description.en or existing.description.en,
                ru=new.description.ru or existing.description.ru,
            ),
            genres=new.genres or existing.genres,
            updated_at=new.updated_at,
        )
        if not result:
            logger.error(
                f"Failed to update existing title {existing.id} in the database."
            )

    async def _create_new_title(self, title: Title, proxy: Optional[str]) -> None:
        """Create new title with downloaded covers."""
        if title.cover and title.cover.url:
            # Download and save covers
            covers_data = await self._media_manager.save_cover(
                image_url=title.cover.url,
                provider=title.source_provider.name,
                content_id=title.source_id,
                proxy=(
                    proxy if title.source_provider != SourceProvider.REMANGA else None
                ),
            )

            if covers_data:
                title.cover = TitleCover(
                    url=covers_data[0],
                    small_url=covers_data[1],
                    large_url=covers_data[2],
                )

            if self._media_manager.http_client.closed:
                logger.warning(
                    f"HTTP session is closed, skipping title creation for {title.id}"
                )
                return

        # Save title to database
        result = await TitleCRUD.create.upsert(title)
        if not result:
            logger.error(f"Failed to create title: {title.id}.")

    # async def _translate_title(self, title: Title, api_key: str, proxy: str) -> None:
    #     if title.description.en and not title.description.ru:
    #         # Translate English description to Russian
    #         translation_data = {
    #             "description": title.description.en,
    #         }
    #         if title.name_en and not title.name_ru:
    #             translation_data["title"] = title.name_en

    #         data = await self._translator.translate(
    #             text=translation_data,
    #             target_lang=Language.RU,
    #             openai_api_key=api_key,
    #             proxy=proxy,
    #         )

    #         if not data:
    #             return

    #         if "description" in data:
    #             title.description = TitleDescription(
    #                 en=title.description.en,
    #                 ru=data["description"],
    #             )
    #         if "title" in data and not title.name_ru:
    #             title.name_ru = data["title"]
    #     elif title.description.ru and not title.description.en:
    #         # Translate Russian description to English
    #         translation_data = {
    #             "description": title.description.ru,
    #         }
    #         if title.name_ru and not title.name_en:
    #             translation_data["title"] = title.name_ru

    #         data = await self._translator.translate(
    #             text=translation_data,
    #             target_lang=Language.EN,
    #             openai_api_key=api_key,
    #             proxy=proxy,
    #         )

    #         if not data:
    #             return

    #         if "description" in data:
    #             title.description = TitleDescription(
    #                 en=data["description"],
    #                 ru=title.description.ru,
    #             )
    #         if "title" in data and not title.name_en:
    #             title.name_en = data["title"]

    async def cleanup(self) -> None:
        """Cleanup resources used by the worker."""
        # Close all http clients and managers
        await self._remanga_client.close()
        await self._mal_client.close()
        await self._media_manager.close()
        # await self._translator.close()
