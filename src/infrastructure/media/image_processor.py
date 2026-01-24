from PIL import Image, ImageOps

from dataclasses import dataclass
from io import BytesIO
from typing import Any
import asyncio


@dataclass
class ImageVariant:
    size_name: str
    content: bytes
    format: str


class ImageProcessor:
    """
    Processor for handling image resizing and format conversion.
    """

    _FORMAT_SAVE_OPTIONS: dict[str, dict[str, Any]] = {
        "WEBP": {
            "quality": None,
            "method": 6,
            "lossless": False,
        },
        "JPEG": {
            "quality": None,
            "optimize": True,
            "progressive": True,
        },
        "PNG": {
            "optimize": True,
            "compress_level": 6,
        },
    }

    def __init__(
        self,
        quality: int = 95,
        output_format: str = "webp",
    ) -> None:
        if not 1 <= quality <= 100:
            raise ValueError("Quality must be between 1 and 100")

        self.quality = quality
        self.output_format = output_format.upper()

    def resize(self, image_data: bytes, size: tuple[int, int]) -> bytes:
        """Resize the image to the specified size while maintaining aspect ratio."""
        with BytesIO(image_data) as image_buffer, Image.open(image_buffer) as img:
            converted = self._ensure_color_mode(img)

            resized = ImageOps.contain(converted, size, Image.Resampling.LANCZOS)
            try:
                return self.save_to_bytes(resized)
            finally:
                resized.close()
                if converted != img:
                    converted.close()

    def create_variants(
        self, image_data: bytes, variants: dict[str, tuple[int, int]]
    ) -> list[ImageVariant]:
        """Create multiple resized variants of the image."""
        results = []

        for size_name, target_size in variants.items():
            resized_data = self.resize(image_data, target_size)
            results.append(
                ImageVariant(
                    size_name=size_name,
                    content=resized_data,
                    format=self.output_format,
                )
            )

        return results

    async def create_variants_async(
        self, image_data: bytes, variants: dict[str, tuple[int, int]]
    ) -> list[ImageVariant]:
        """Asynchronous wrapper for create_variants method."""
        return await asyncio.to_thread(self.create_variants, image_data, variants)

    def save_to_bytes(self, image: Image.Image) -> bytes:
        """Save the image to bytes with the specified format and quality."""
        save_options = self._FORMAT_SAVE_OPTIONS[self.output_format].copy()

        if "quality" in save_options:
            save_options["quality"] = self.quality

        with BytesIO() as output_buffer:
            image.save(
                output_buffer,
                format=self.output_format,
                **save_options,
            )
            return output_buffer.getvalue()

    def _ensure_color_mode(self, img: Image.Image) -> Image.Image:
        if self.output_format in ("WEBP", "PNG") and img.mode == "RGBA":
            target_mode = "RGBA"
        else:
            target_mode = "RGB"

        if img.mode != target_mode:
            return img.convert(target_mode)

        return img
