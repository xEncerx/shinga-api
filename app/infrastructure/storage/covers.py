from typing import Literal
from pathlib import Path
from PIL import Image
import aiofiles
import asyncio
import hashlib
# import base64
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

    def generate_filename(
        self,
        provider: str,
        content_id: str,
        size: Literal["", "s", "l"] = "",
    ) -> str:
        """
        Generating a file name using a template: provider_id_size.webp

        Args:
            provider (str): Provider name (mal, shiki, etc)
            content_id (str): Provider's content ID
            size (str): Size: "" (original), "s" (small), "l" (large)

        :return: Generated filename in sha1 format with .webp extension
        """
        raw_name = f"{provider}_{content_id}_{size}".strip("_")
        encoded = hashlib.sha1(raw_name.encode()).hexdigest()[:12]
        return f"{encoded}.webp"

        # encoded = base64.b32encode(raw_name.encode()).decode().lower()
        # return encoded.rstrip("=") + ".webp"

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
        force_redownload: bool = False,
        proxy: str | None = None,
    ) -> list[str]:
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
            return [settings.COVER_404_URL] * 3

        # Empty image in MAL
        if image_url.endswith("apple-touch-icon-256.png"):
            return [settings.COVER_404_URL] * 3

        filename = self.generate_filename(provider, content_id, "l")
        filepath = self.storage_path / filename
        if filepath.exists() and not force_redownload:
            return [
                f"{settings.COVER_PUBLIC_PATH}/{self.generate_filename(provider, content_id, size_name)}"  # type: ignore
                for size_name in self.SIZE_MAP.keys()
            ]

        image_data = await self._download_image(image_url, proxy=proxy)
        if not image_data:
            return [settings.COVER_404_URL] * 3

        result = []
        for size_name, size in self.SIZE_MAP.items():
            filename = self.generate_filename(provider, content_id, size_name)  # type: ignore
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
                result.append(settings.COVER_404_URL)

        return result

    async def batch_save(
        self,
        images: list[tuple[str | None, str, str]],
        force_redownload: bool = False,
        proxy: str | None = None,
    ) -> list[list[str]]:
        """
        Batch process and save multiple cover images.

        Args:
            images: List of tuples (image_url, provider, content_id)
            force_redownload (bool): Whether to overwrite existing files
            proxy (str | None): Optional proxy URL for HTTP requests

        :return: List of lists containing public URLs for each image in all three sizes
        """
        tasks = [
            self.save_cover(image_url, provider, content_id, force_redownload, proxy)
            for image_url, provider, content_id in images
        ]
        return await asyncio.gather(*tasks)
