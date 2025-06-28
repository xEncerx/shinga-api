from abc import ABC, abstractmethod

from ..infrastructure.db.models import Title
from app.utils import AsyncHttpClient


class BaseProvider(ABC, AsyncHttpClient):
    """
    Base class for all providers.
    Providers should inherit from this class and implement the required methods.
    """

    def __init__(
        self,
        base_url: str | None = None,
        timeout: float = 15.0,
    ):
        """
        Initialize the provider with any necessary arguments.

        Args:
            base_url: Base URL for the API
            timeout: Timeout for requests in seconds
        """
        super().__init__(
            base_url=base_url,
            timeout=timeout,
            disable_ssl=True,
        )

    @abstractmethod
    async def get_by_id(id: int | str, proxy: str | None) -> Title | None:  # type: ignore
        """
        Method for retrieving title data from a specified provider by id.
        """
        pass