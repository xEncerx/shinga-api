from typing import Generic, TypeVar
from pydantic import BaseModel

__all__ = ["Pagination", "TitlePagination"]


T = TypeVar("T")


class PaginationItems(BaseModel):
    """Pagination items metadata."""

    count: int = 0
    total: int = 0
    per_page: int = 0


class Pagination(BaseModel):
    """Pagination metadata."""

    last_visible_page: int = 0
    has_next_page: bool = False
    current_page: int = 0
    items: PaginationItems = PaginationItems()


class TitlePagination(BaseModel, Generic[T]):
    """Paginated response model for titles."""

    pagination: Pagination = Pagination()
    data: list[T] = []
