from abc import ABC, abstractmethod
from typing import Any

from ..infrastructure.db.models import *
from app.domain.models import *


class BaseParserProvider(ABC):
    """
    Base class for provider parsers.
    This class should be inherited by all provider parsers.
    """

    @staticmethod
    @abstractmethod
    def parse(data: dict[str, Any]) -> Title:
        """
        Parse the raw data from the provider into a Title model.
        This method should be implemented by subclasses to handle specific parsing logic.
        """
        ...

    @staticmethod
    @abstractmethod
    def parse_page(data: dict[str, Any]) -> TitlePagination:
        """
        Parse a page of raw data from the provider into a TitlePagination model.
        This method should be implemented by subclasses to handle specific pagination parsing logic.
        """
        ...