from abc import ABC, abstractmethod
from typing import Any

from app.infrastructure.db.models import *
from app.infrastructure.db.utils import *
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

    @classmethod
    @abstractmethod
    def parse_page(cls, data: dict[str, Any]) -> TitlePagination:
        """
        Parse a page of raw data from the provider into a TitlePagination model.
        This method should be implemented by subclasses to handle specific pagination parsing logic.
        """
        ...