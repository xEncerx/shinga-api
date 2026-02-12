from pydantic import BaseModel, Field
from typing import Generic, TypeVar

__all__ = [
    "BaseContentResponse",
    "PaginatedContentResponse",
    "PaginationResponse",
    "PaginationItemsResponse",
]

T = TypeVar("T")


class PaginationItemsResponse(BaseModel):
    """Pagination items metadata."""

    count: int = 0
    total: int = 0
    per_page: int = 0


class PaginationResponse(BaseModel):
    """Pagination metadata."""

    last_visible_page: int = 0
    has_next_page: bool = False
    current_page: int = 0
    items: PaginationItemsResponse = PaginationItemsResponse()


class BaseContentResponse(BaseModel, Generic[T]):
    """Base response model for content-related endpoints."""

    content: T = Field(
        ...,
        description="Content data with dynamic structure depending on the endpoint",
    )


class PaginatedContentResponse(BaseModel, Generic[T]):
    """Base response model for paginated content-related endpoints."""

    content: T = Field(
        ...,
        description="Content data with dynamic structure depending on the endpoint",
    )
    pagination: PaginationResponse = PaginationResponse()
