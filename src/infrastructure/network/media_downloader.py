from dataclasses import dataclass

from .client import AsyncHttpClient

__all__ = ["MediaDownloader", "MediaFile"]


@dataclass
class MediaFile:
    """Represents a downloaded media file."""

    content: bytes
    content_type: str
    url: str
    size: int

    @property
    def extension(self) -> str:
        """Get the file extension based on the content type."""
        mime_to_ext = {
            "image/jpeg": "webp",
            "image/png": "webp",
            "image/webp": "webp",
            "image/gif": "gif",
            "video/webm": "webm",
            "video/mp4": "webm",
        }
        return mime_to_ext.get(self.content_type, "bin")

    @property
    def is_image(self) -> bool:
        """Check if the media file is an image."""
        return self.content_type.startswith("image/")

    @property
    def is_video(self) -> bool:
        """Check if the media file is a video."""
        return self.content_type.startswith("video/")


class MediaDownloader(AsyncHttpClient):
    """A client for downloading media files over HTTP."""

    async def download(self, url: str) -> MediaFile:
        """Download media content from the given URL and return it as bytes."""
        async with self.get(url) as response:
            content = await response.read()
            content_type = (
                response.headers.get("Content-Type", "").split(";")[0].strip()
            )

            if not content_type:
                raise ValueError(f"Missing Content-Type header for {url}")

            size = len(content)
            return MediaFile(
                content=content,
                content_type=content_type,
                url=url,
                size=size,
            )
