from dataclasses import dataclass

from src.domain.interfaces import IFileStorage, ITitleRepository
from src.domain.services import MediaHashGenerator
from src.domain.models.titles import TitleCover
from src.infrastructure.media import ImageProcessor
from src.infrastructure.network import MediaDownloader
from src.domain.models.source import Source
from src.core import settings


@dataclass
class ProcessImageResult:
    source: str
    external_id: str


class ProcessImageUseCase:
    """
    Use case for processing and storing cover images.
    """

    def __init__(
        self,
        title_repository: ITitleRepository,
        downloader: MediaDownloader,
        storage: IFileStorage,
        processor: ImageProcessor,
    ) -> None:
        self._title_repo = title_repository
        self._downloader = downloader
        self._processor = processor
        self._storage = storage

    async def execute(
        self,
        master_title_id: int,
        cover_url: str,
        source: Source,
        external_id: str,
    ) -> ProcessImageResult:
        """
        Process and store cover image, returning public URLs for each variant.

        Args:
            cover_url (str): URL of the cover image to process. USE HIGH-RESOLUTION IMAGE IF POSSIBLE.
            source (Source): Source enum value representing the source (e.g., Source.MAL, Source.SHIKIMORI).
            external_id (str): External identifier for the title.
        """
        result = ProcessImageResult(source=source.value, external_id=external_id)
        file_hash = MediaHashGenerator.generate_cover_hash(source.value, external_id)

        # 1. Check if image variants already exist
        check_image_size = list(settings.COVER_VARIANTS.keys())[0]
        check_image_path = self._format_file(file_hash, check_image_size)

        if await self._storage.exists(check_image_path):
            # 1.1 Variants already exist, build URLs
            paths = await self._build_exists_paths(file_hash)
        else:
            # 2. Download image
            image_bytes = await self._downloader.download(cover_url)

            # 3. Process variants
            variants = await self._processor.create_variants_async(
                image_bytes.content,
                settings.COVER_VARIANTS,
            )

            # 4. Store variants and build URLs
            paths = {}
            for variant in variants:
                path = self._format_file(file_hash, variant.size_name)
                await self._storage.save(path, variant.content)
                paths[variant.size_name] = await self._storage.get_public_url(path)

        # 5. Update the master title with the cover URLs
        await self._title_repo.update_master_title_cover(
            master_title_id=master_title_id,
            cover=TitleCover(**paths),
        )

        return result

    async def _build_exists_paths(self, file_hash: str) -> dict[str, str]:
        return {
            size: await self._storage.get_public_url(
                self._format_file(file_hash, size),
            )
            for size in settings.COVER_VARIANTS.keys()
        }

    def _format_file(self, file_hash: str, size: str) -> str:
        return f"{file_hash}_{size}.{settings.BASE_IMAGE_FORMAT}"
