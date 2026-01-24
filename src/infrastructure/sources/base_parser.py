from abc import ABC, abstractmethod
from datetime import datetime

from src.domain.models.titles import (
    TitlePagination,
    SourceTitleData,
    SourceMetadata,
    TitleCategory,
    TitleStatus,
    TitleGenre,
    TitleCover,
    TitleType,
    Pagination,
    TitleData,
)
from src.domain.models import Source
from .utils import tag_remover

__all__ = [
    "TitlePagination",
    "SourceTitleData",
    "SourceMetadata",
    "TitleCategory",
    "tag_remover",
    "Pagination",
    "TitleGenre",
    "TitleStatus",
    "BaseParser",
    "TitleData",
    "TitleCover",
    "TitleType",
    "datetime",
    "Source",
]


class BaseParser(ABC):
    """
    Interface for parsers that convert raw data into structured title data.
    """

    @staticmethod
    @abstractmethod
    def parse_title(data: dict) -> SourceTitleData:
        """
        Method for parsing title data from a dictionary.
        """
        raise NotImplementedError("This method should be implemented by subclasses.")

    @staticmethod
    @abstractmethod
    def parse_page(data: dict) -> list[SourceTitleData]:
        """
        Method for parsing a page of title data from a dictionary.
        """
        raise NotImplementedError("This method should be implemented by subclasses.")

    @staticmethod
    @abstractmethod
    def convert_type(data: str) -> TitleType:
        """
        Method for converting a string representation of a title type to a TitleType enum.
        """
        raise NotImplementedError("This method should be implemented by subclasses.")

    @staticmethod
    @abstractmethod
    def convert_status(data: str) -> TitleStatus:
        """
        Method for converting a string representation of a title status to a TitleStatus enum.
        """
        raise NotImplementedError("This method should be implemented by subclasses.")

    @staticmethod
    @abstractmethod
    def convert_genre(data: str) -> TitleGenre:
        """
        Method for converting a string representations of genre to a TitleGenre enums.
        """
        raise NotImplementedError("This method should be implemented by subclasses.")

    @staticmethod
    @abstractmethod
    def convert_category(data: str) -> TitleCategory:
        """
        Method for converting a string representations of category to a TitleCategory enums.
        """
        raise NotImplementedError("This method should be implemented by subclasses.")
