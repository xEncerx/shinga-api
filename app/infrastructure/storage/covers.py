from typing import Literal
from pathlib import Path
from PIL import Image
import aiofiles
import asyncio
import base64
import io

from app.core import settings, logger
from app.utils import AsyncHttpClient


class CoverManger(AsyncHttpClient):
    """
    Manages cover image downloads, processing, and storage.

    Attributes:
        storage_path (Path): Directory where cover images are stored
        _client (AsyncClient): HTTP client for downloading images
    """

    def __init__(
        self,
        storage_path: str = settings.COVER_STORAGE_PATH,
        proxy: str | None = None,
        timeout: int = 10,
    ) -> None:
        """
        Initialize the CoverManager.

        Args:
            storage_path (str): Directory path where cover images will be stored
            proxy (str | None): Optional proxy URL for HTTP requests
            timeout (int): Request timeout in seconds
        """

        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

        self.SIZE_MAP = {"": (225, 319), "s": (112, 160), "l": (423, 600)}

        super().__init__(proxy=proxy, timeout=timeout)

    async def __aenter__(self) -> "CoverManger":
        await super().__aenter__()
        return self

    def _generate_filename(
        self,
        provider: str,
        content_id: str,
        size: Literal["", "s", "l"] = "",
    ) -> str:
        """
        Generating a file name using a template: provider_id_size.webp

        Args:
            provider (str): Provider ID (mal, shiki, etc)
            content_id (str): Provider's content ID
            size (str): Size: "" (original), "s" (small), "l" (large)

        :return: Generated filename in base32 format with .webp extension
        """
        raw_name = f"{provider}_{content_id}_{size}".strip("_")
        encoded = base64.b32encode(raw_name.encode()).decode().lower()
        return encoded.rstrip("=") + ".webp"

    async def _download_image(
        self,
        url: str,
        proxy: str | None = None,
    ) -> bytes | None:
        """
        Download an image from a given URL.

        Args:
            url (str): The URL of the image to download
            proxy (str | None): Optional proxy URL for the request

        :return: Image data as bytes, or None if download failed
        """
        try:
            return await self.get(
                url=url,
                response_type="bytes",
                proxy=proxy,
            )
        except Exception as e:
            logger.error(f"Error downloading image from {url}: {e}")

    def _process_image(
        self,
        image_data: bytes,
        target_size: tuple[int, int] | None = None,
    ) -> bytes:
        """
        Convert image to WebP format and optionally resize it.

        Args:
            image_data (bytes): Bytes of the original image
            target_size (tuple[int, int]): Optional target size as (width, height) tuple

        :return: Processed image data in WebP format as bytes
        """
        with (
            io.BytesIO(image_data) as input_buffer,
            Image.open(input_buffer) as img,
            io.BytesIO() as output_buffer,
        ):
            if img.size == target_size:
                return image_data

            if img.mode == "RGBA":
                img = img.convert("RGB")

            if target_size:
                img.thumbnail(target_size, Image.Resampling.LANCZOS)

            img.save(output_buffer, format="WEBP", quality=95)

            return output_buffer.getvalue()

    async def save_cover(
        self,
        image_url: str | None,
        provider: str,
        content_id: str,
        size_type: Literal["", "s", "l"] = "",
        force_redownload: bool = False,
        proxy: str | None = None,
    ) -> str | None:
        """
        Download, process and save a cover image.

        Args:
            image_url str | None: URL of the source image
            provider (str): Provider name (e.g., "mal", "shiki")
            content_id (str): Unique content identifier
            size_type (str): Size variant - "" (original = 225x319), "s" (small = 112x160), "l" (large = 423x600)
            force_redownload (bool): Whether to overwrite existing files
            proxy (str | None): Optional proxy URL for HTTP requests

        :return: Public URL of the saved cover, or None if processing failed
        """
        if not image_url:
            return

        filename = self._generate_filename(provider, content_id, size_type)
        filepath = self.storage_path / filename

        if filepath.exists() and not force_redownload:
            return f"{settings.COVER_PUBLIC_PATH}/{filename}"

        target_size = self.SIZE_MAP[size_type]

        try:
            image_data = await self._download_image(image_url, proxy=proxy)
            if not image_data:
                return

            processed_data = self._process_image(image_data, target_size)

            async with aiofiles.open(filepath, "wb") as f:
                await f.write(processed_data)

            return f"{settings.COVER_PUBLIC_PATH}/{filename}"

        except Exception as e:
            if filepath.exists():
                filepath.unlink()
            raise RuntimeError(f"Failed to process cover: {str(e)}")

    async def save_cover_all_size(
        self,
        image_url: str | None,
        provider: str,
        content_id: str,
        force_redownload: bool = False,
        proxy: str | None = None,
    ) -> list[str | None]:
        """
        Process a single image into all three size variants and save them.

        Args:
            image_url (str | None): URL of the source image
            provider (str): Provider name (e.g., "mal", "shiki")
            content_id (str): Unique content identifier
            force_redownload (bool): Whether to overwrite existing files
            proxy (str | None): Optional proxy URL for HTTP requests

        :return: List of public URLs for all three size variants in order [original, small, large]
        """
        if not image_url:
            return [None, None, None]

        image_data = await self._download_image(image_url, proxy=proxy)
        if not image_data:
            return [None, None, None]

        result = []
        for name, size in self.SIZE_MAP.items():
            filename = self._generate_filename(provider, content_id, name)  # type: ignore
            filepath = self.storage_path / filename

            if filepath.exists() and not force_redownload:
                result.append(f"{settings.COVER_PUBLIC_PATH}/{filename}")
                continue

            try:
                processed_data = self._process_image(image_data, size)

                async with aiofiles.open(filepath, "wb") as f:
                    await f.write(processed_data)

                result.append(f"{settings.COVER_PUBLIC_PATH}/{filename}")
            except Exception as e:
                logger.error(f"Failed to process cover size {size}: {str(e)}")
                if filepath.exists():
                    filepath.unlink()
                result.append(None)

        return result

    async def batch_save(
        self,
        images: list[tuple[str | None, str, str]],
        force_redownload: bool = False,
        proxy: str | None = None,
    ) -> list[list[str | None]]:
        """
        Batch process and save multiple cover images.

        Args:
            images: List of tuples (image_url, provider, content_id)
            force_redownload (bool): Whether to overwrite existing files
            proxy (str | None): Optional proxy URL for HTTP requests

        :return: List of lists containing public URLs for each image in all three sizes
        """
        tasks = [
            self.save_cover_all_size(image_url, provider, content_id, force_redownload, proxy)
            for image_url, provider, content_id in images
        ]
        return await asyncio.gather(*tasks)