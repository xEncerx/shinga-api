from abc import ABC, abstractmethod


class IFileStorage(ABC):
    """Interface for file storage operations."""

    @abstractmethod
    async def save(self, path: str, file_data: bytes) -> str:
        """Save a file and return its storage path."""
        raise NotImplementedError("Method 'save' not implemented")

    @abstractmethod
    async def read(self, path: str) -> bytes:
        """Read a file from storage and return its data."""
        raise NotImplementedError("Method 'read' not implemented")

    @abstractmethod
    async def exists(self, path: str) -> bool:
        """Check if a file exists at the given path."""
        raise NotImplementedError("Method 'exists' not implemented")

    @abstractmethod
    async def delete(self, path: str) -> bool:
        """Delete a file from storage and return success status."""
        raise NotImplementedError("Method 'delete' not implemented")

    @abstractmethod
    async def get_public_url(self, path: str) -> str:
        """Get a public URL for the file at the given path."""
        raise NotImplementedError("Method 'get_public_url' not implemented")
