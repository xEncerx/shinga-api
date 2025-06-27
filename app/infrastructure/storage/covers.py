from httpx import AsyncClient
from typing import Literal
from pathlib import Path
from PIL import Image
import aiofiles
import asyncio
import base64
import io

from app.core import settings, logger


class CoverManger:
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
            storage_path: Directory path where cover images will be stored
            proxy: Optional proxy URL for HTTP requests
            timeout: Request timeout in seconds
        """

        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

        self._client = AsyncClient(
            proxy=proxy,
            timeout=timeout,
        )

    async def close(self) -> None:
        """Close the HTTP client and clean up resources."""
        await self._client.aclose()

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()

    def _generate_filename(
        self,
        provider: str,
        content_id: str,
        size: Literal["", "s", "l"] = "",
    ) -> str:
        """
        Generating a file name using a template: provider_id_size.webp

        Args:
            provider: Provider ID (mal, shiki, etc)
            content_id: Provider's content ID
            size: Size: "" (original), "s" (small), "l" (large)

        :return: Generated filename in base32 format with .webp extension
        """
        raw_name = f"{provider}_{content_id}_{size}".strip("_")
        encoded = base64.b32encode(raw_name.encode()).decode().lower()
        return encoded.rstrip("=") + ".webp"

    async def _download_image(self, url: str) -> bytes | None:
        """
        Download an image from a given URL.

        Args:
            url: The URL of the image to download

        :return: Image data as bytes, or None if download failed
        """
        try:
            response = await self._client.get(
                url,
                follow_redirects=True,
            )
            response.raise_for_status()
            return response.content
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
            image_data: Bytes of the original image
            target_size: Optional target size as (width, height) tuple

        :return: Processed image data in WebP format as bytes
        """
        with (
            io.BytesIO(image_data) as input_buffer,
            Image.open(input_buffer) as img,
            io.BytesIO() as output_buffer,
        ):
            if img.mode == "RGBA":
                img = img.convert("RGB")

            if target_size:
                img.thumbnail(target_size, Image.Resampling.LANCZOS)

            img.save(output_buffer, format="WEBP", quality=85, method=6)

            return output_buffer.getvalue()

    async def save_cover(
        self,
        image_url: str | None,
        provider: str,
        content_id: str,
        size_type: Literal["", "s", "l"] = "",
        force_redownload: bool = False,
    ) -> str | None:
        """
        Download, process and save a cover image.

        Args:
            image_url: URL of the source image
            provider: Provider name (e.g., "mal", "shiki")
            content_id: Unique content identifier
            size_type: Size variant - "" (original = no resizing), "s" (small = 42x60), "l" (large = 423x600)
            force_redownload: Whether to overwrite existing files

        :return: Public URL of the saved cover, or None if processing failed
        """
        if not image_url: return

        size_map = {"": None, "s": (42, 60), "l": (423, 600)}
        target_size = size_map[size_type]

        filename = self._generate_filename(provider, content_id, size_type)
        filepath = self.storage_path / filename

        if filepath.exists() and not force_redownload:
            return f"{settings.COVER_PUBLIC_PATH}/{filename}"

        try:
            image_data = await self._download_image(image_url)
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

    async def batch_save(
        self,
        tasks: list[tuple[str | None, str, str, str]],
        max_concurrent: int = 10,
    ) -> list[str | None]:
        """
        Process multiple cover images concurrently.

        Args:
            tasks: List of tuples containing (image_url, provider, content_id, size_type)
            max_concurrent: Maximum number of simultaneous download/processing operations

        :return: List of public URLs for successfully processed covers, None for failed ones
        """
        semaphore = asyncio.Semaphore(max_concurrent)
        results = []

        async def process_task(task):
            """
            Process a single cover task with concurrency control.

            Args:
                task: Tuple containing (image_url, provider, content_id, size_type)
            """
            async with semaphore:
                try:
                    url = await self.save_cover(*task)
                    results.append(url)
                except Exception as e:
                    print(f"Error processing {task}: {e}")
                    results.append(None)

        await asyncio.gather(*(process_task(task) for task in tasks))
        return results
