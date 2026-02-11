from pydantic import BaseModel

__all__ = ["Pagination", "PaginationItems"]


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
