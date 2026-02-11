from pathlib import Path
import aiofiles

from src.domain.interfaces import IFileStorage

__all__ = ["LocalFileStorage"]


class LocalFileStorage(IFileStorage):
    """A local file storage implementation using the filesystem."""

    def __init__(self, base_path: Path | str, public_url_prefix: str) -> None:
        """
        Initialize the local file storage.

        Args:
            base_path (Path | str): The base directory for storing files.
            public_url_prefix (str): The public URL prefix for accessing stored files.
        """
        self._base_path = Path(base_path).resolve()
        self._base_path.mkdir(parents=True, exist_ok=True)
        self._public_url_prefix = public_url_prefix.rstrip("/")

    async def save(self, path: str, file_data: bytes) -> str:
        full_path = self._resolve_path(path)
        full_path.parent.mkdir(parents=True, exist_ok=True)

        async with aiofiles.open(full_path, "wb") as f:
            await f.write(file_data)

        return str(full_path.relative_to(self._base_path))

    async def read(self, path: str) -> bytes:
        full_path = self._resolve_path(path)

        if not full_path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        async with aiofiles.open(full_path, "rb") as f:
            return await f.read()

    async def exists(self, path: str) -> bool:
        full_path = self._resolve_path(path)
        return full_path.exists()

    async def delete(self, path: str) -> bool:
        full_path = self._resolve_path(path)

        if not full_path.exists():
            return False

        full_path.unlink()
        return True

    async def get_public_url(self, path: str) -> str:
        path = path.lstrip("/")
        return f"{self._public_url_prefix}/{path}"

    def _resolve_path(self, relative_path: str) -> Path:
        """Resolve a relative path against the base storage path."""
        relative_path = relative_path.lstrip("/")

        full_path = (self._base_path / relative_path).resolve()

        if not full_path.is_relative_to(self._base_path):
            raise ValueError(f"Path traversal detected: {relative_path}")

        return full_path
