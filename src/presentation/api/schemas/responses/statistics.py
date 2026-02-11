from pydantic import BaseModel, Field, model_validator

from src.domain.models import TitleBookmark

__all__ = ["UserStatisticsResponse", "BookmarkStatisticsResponse", "RatingStatisticsResponse"]

class BookmarkStatisticsResponse(BaseModel):
    bookmarks: dict[TitleBookmark, int] = Field(
        description="A mapping of bookmark types to their respective counts",
    )
    total: int = Field(default=0, description="Total number of bookmarks")


class RatingStatisticsResponse(BaseModel):
    average_rating: float = Field(
        default=0.0,
        description="The average rating given by the user",
    )
    ratings_count: int = Field(
        default=0,
        description="Total number of ratings given",
    )
    ratings_distribution: dict[int, int] = Field(
        description="A mapping of rating values (1-10) to their respective counts",
    )

    @model_validator(mode="after")
    def fill_ratings_distribution(self) -> "RatingStatisticsResponse":
        """Ensure all ratings from 1 to 10 are present in the distribution"""
        full_distribution = {rating: 0 for rating in range(1, 11)}
        full_distribution.update(self.ratings_distribution)
        self.ratings_distribution = full_distribution
        return self


class UserStatisticsResponse(BaseModel):
    bookmarks: BookmarkStatisticsResponse = Field(
        description="Statistics related to user bookmarks",
    )
    ratings: RatingStatisticsResponse = Field(
        description="Statistics related to user ratings",
    )
