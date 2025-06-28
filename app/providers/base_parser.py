from abc import ABC, abstractmethod
from typing import Any

from ..infrastructure.db.models import *


class BaseParserProvider(ABC):
    """
    Base class for provider parsers.
    This class should be inherited by all provider parsers.
    """

    @staticmethod
    @abstractmethod
    async def parse(data: dict[str, Any]) -> Title:
        """
        Parse the raw data from the provider into a Title model.
        This method should be implemented by subclasses to handle specific parsing logic.
        """
        ...
