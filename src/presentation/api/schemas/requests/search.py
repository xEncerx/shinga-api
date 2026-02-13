from pydantic import BaseModel, Field, field_validator

from src.domain.models import (
    TitleGenre,
    TitleCategory,
    TitleType,
    TitleStatus,
    SortingOrder,
    TitleSortBy,
    TitleBookmark,
)

__all__ = ["TitleSearchRequest"]


class TitleSearchRequest(BaseModel):
    query: str | None = Field(default=None, description="Search query string")

    # Filter Fields
    type: TitleType | None = Field(
        default=None,
        description="Filter by title type (e.g., manga, manhwa, etc.)",
    )
    status: TitleStatus | None = Field(
        default=None,
        description="Filter by title status (e.g., ongoing, finished, etc.)",
    )
    genres: list[str] | None = Field(
        default=None,
        description="Filter by genres (e.g., action, comedy, etc.)",
    )
    categories: list[str] | None = Field(
        default=None,
        description="Filter by categories (e.g., shounen, seinen, etc.)",
    )
    bookmark: TitleBookmark | None = Field(
        default=None,
        description="Filter by user's bookmark status (e.g., reading, completed, etc.)",
    )
    min_rating: float | None = Field(
        default=None,
        ge=0,
        le=10,
        description="Filter by minimum rating (0 to 10)",
    )
    max_rating: float | None = Field(
        default=None,
        ge=0,
        le=10,
        description="Filter by maximum rating (0 to 10)",
    )
    min_chapters: int | None = Field(
        default=None,
        ge=0,
        description="Filter by minimum number of chapters",
    )
    max_chapters: int | None = Field(
        default=None,
        ge=0,
        description="Filter by maximum number of chapters",
    )

    # Sorting Fields
    order: SortingOrder = Field(
        default=SortingOrder.DESC, description="Sorting order (asc or desc)"
    )
    sort_by: TitleSortBy = Field(
        default=TitleSortBy.RATING,
        description="Field to sort by (e.g., rating, popularity, chapters, views, favorites)",
    )

    # Pagination Fields
    page: int = Field(default=1, ge=1, description="Page number for pagination")
    page_size: int = Field(
        default=27,
        ge=1,
        le=50,
        description="Number of items per page for pagination",
    )

    @field_validator("genres", mode="before")
    @classmethod
    def parse_genres(cls, v):
        """Validate genres."""
        if v is None:
            return None
        if isinstance(v, list):
            try:
                return [TitleGenre[genre.upper()].name for genre in v if genre]
            except KeyError as e:
                raise ValueError(f"Invalid genre: {e.args[0]}")
        return v

    @field_validator("categories", mode="before")
    @classmethod
    def parse_categories(cls, v):
        """Validate categories."""
        if v is None:
            return None
        if isinstance(v, list):
            try:
                return [
                    TitleCategory[category.upper()].name for category in v if category
                ]
            except KeyError as e:
                raise ValueError(f"Invalid category: {e.args[0]}")
        return v
