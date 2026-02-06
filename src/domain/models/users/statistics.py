from pydantic import BaseModel, Field

from src.domain.models.titles.relations import TitleBookmark

__all__ = [
    "BookmarkStatistics",
    "RatingStatistics",
    "UserStatistics",
]


class BookmarkStatistics(BaseModel):
    bookmarks: dict[TitleBookmark, int] = Field(
        default_factory=lambda: {k: 0 for k in TitleBookmark},
        description="A mapping of bookmark types to their respective counts",
    )
    total: int = Field(default=0, description="Total number of bookmarks")


class RatingStatistics(BaseModel):
    average_rating: float = Field(
        default=0.0,
        description="The average rating given by the user",
    )
    ratings_count: int = Field(
        default=0,
        description="Total number of ratings given",
    )
    ratings_distribution: dict[int, int] = Field(
        default_factory=lambda: {i: 0 for i in range(1, 11)},
        description="A mapping of rating values (1-10) to their respective counts",
    )


class UserStatistics(BaseModel):
    bookmarks: BookmarkStatistics = Field(
        default_factory=BookmarkStatistics,
        description="Statistics related to user bookmarks",
    )
    ratings: RatingStatistics = Field(
        default_factory=RatingStatistics,
        description="Statistics related to user ratings",
    )
