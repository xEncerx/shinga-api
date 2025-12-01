from abc import ABC, abstractmethod
from typing import Any

from app.domain.models.title_data import *
from app.infrastructure.db.utils import *
from app.utils import tag_remover
from app.domain.models import *
from app.domain.enums import *
from app.core import logger


class BaseParserProvider(ABC):
    """
    Base class for provider parsers.
    This class should be inherited by all provider parsers.
    """

    @staticmethod
    @abstractmethod
    def parse(data: dict[str, Any]) -> TitleData:
        """
        Parse the raw data from the provider into a Title model.
        This method should be implemented by subclasses to handle specific parsing logic.
        """
        raise NotImplementedError("This method should be implemented by subclasses.")

    @classmethod
    @abstractmethod
    def parse_page(cls, data: dict[str, Any]) -> TitlePagination[TitleData]:
        """
        Parse a page of raw data from the provider into a TitlePagination model.
        This method should be implemented by subclasses to handle specific pagination parsing logic.
        """
        raise NotImplementedError("This method should be implemented by subclasses.")
