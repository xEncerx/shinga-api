from pydantic import BaseModel, Field
from datetime import datetime

from src.domain.models.titles.relations import (
    TitleType,
    TitleStatus,
    TitleCover,
    TitleBookmark,
)
from src.domain.models import TitleData, UserTitleData
from .forms import TitleGenreForm, TitleCategoryForm
from .base import BaseContentResponse, PaginatedContentResponse

__all__ = [
    "TitleResponse",
    "UserTitleDataResponse",
    "TitleWithUserDataResponse",
    "TitleDetailResponse",
    "TitleSearchResponse",
]


class TitleResponse(BaseModel):
    """Response model for title data."""

    id: int = Field(
        description="Unique identifier of the title in the system",
    )
    mal_id: int | None = Field(
        default=None,
        description="MyAnimeList ID, if applicable",
    )
    name_ru: str | None = Field(default=None, description="Title name in Russian")
    name_en: str | None = Field(default=None, description="Title name in English")
    description_ru: str | None = Field(
        default=None, description="Title description in Russian"
    )
    description_en: str | None = Field(
        default=None, description="Title description in English"
    )
    type: TitleType = Field(description="Type of the title (e.g., manga, manhwa, etc.)")
    status: TitleStatus = Field(
        description="Current status of the title (e.g., ongoing, finished, etc.)",
    )
    popularity: int = Field(
        default=0,
        ge=0,
        description="Popularity rank of the title within the source",
    )
    chapters: int = Field(
        default=0,
        ge=0,
        description="Number of chapters available",
    )
    views: int = Field(
        default=0,
        ge=0,
        description="Number of views or reads of the title",
    )
    volumes: int = Field(
        default=0,
        ge=0,
        description="Number of volumes available",
    )
    favorites: int = Field(
        default=0,
        ge=0,
        description="Number of users who have favorited the title",
    )
    rating: float = Field(
        default=0.0,
        ge=0,
        le=10.0,
        description="Average user rating of the title. Value from 0 to 10",
    )
    scored_by: int = Field(
        default=0,
        ge=0,
        description="Number of users who rated the title",
    )
    released_at: datetime | None = Field(
        default=None,
        description="Release date of the title",
    )
    ended_at: datetime | None = Field(
        default=None,
        description="End date of the title",
    )
    genres: list[TitleGenreForm] = Field(
        default=[],
        description="List of genres associated with the title",
    )
    categories: list[TitleCategoryForm] = Field(
        default=[],
        description="List of categories associated with the title",
    )
    authors: list[str] = Field(
        default=[],
        description="List of authors associated with the title",
    )
    alt_names: list[str] = Field(
        default=[],
        description="List of alternative names for the title",
    )
    cover: TitleCover | None = Field(
        default=None,
        description="Cover images of the title in various sizes",
    )

    @classmethod
    def from_domain(cls, title: TitleData) -> "TitleResponse":
        """Create TitleResponse from domain model."""
        return cls(
            id=title.id,  # type: ignore
            mal_id=title.mal_id,
            name_ru=title.name_ru,
            name_en=title.name_en,
            description_ru=title.description_ru,
            description_en=title.description_en,
            type=title.type,
            status=title.status,
            popularity=title.popularity,
            chapters=title.chapters,
            views=title.views,
            volumes=title.volumes,
            favorites=title.favorites,
            rating=title.rating,
            scored_by=title.scored_by,
            released_at=title.released_at,
            ended_at=title.ended_at,
            genres=[
                TitleGenreForm(
                    name=genre.name,
                    ru=genre.ru,
                    en=genre.en,
                )
                for genre in title.genres
            ],
            categories=[
                TitleCategoryForm(
                    name=category.name,
                    ru=category.ru,
                    en=category.en,
                )
                for category in title.categories
            ],
            authors=title.authors,
            alt_names=title.alt_names,
            cover=title.cover,
        )


class UserTitleDataResponse(BaseModel):
    """Response model for user-specific title data."""

    rating: float = Field(
        default=0.0,
        ge=0.0,
        le=10.0,
        description="The user's rating for the title, from 0.0 to 10.0",
    )
    current_url: str | None = Field(
        default=None,
        description="The current URL of the title for the user",
    )
    bookmark: TitleBookmark = Field(
        default=TitleBookmark.NOT_READING,
        description="The bookmark status of the title for the user",
    )
    is_favorite: bool = Field(
        default=False,
        description="Indicates if the title is marked as a favorite by the user",
    )
    note: str | None = Field(
        default=None,
        max_length=200,
        description="User's personal note about the title",
    )
    extended_data: dict | None = Field(
        default=None,
        description="Additional specific data that doesn't fit into predefined fields",
    )

    @classmethod
    def from_domain(cls, user_data: UserTitleData) -> "UserTitleDataResponse":
        """Create UserTitleDataResponse from domain model."""
        return cls(
            rating=user_data.rating,
            current_url=user_data.current_url,
            bookmark=user_data.bookmark,
            is_favorite=user_data.is_favorite,
            note=user_data.note,
            extended_data=user_data.extended_data,
        )


class TitleWithUserDataResponse(BaseModel):
    """Combined response with title and user data."""

    title: TitleResponse
    user_data: UserTitleDataResponse | None = Field(
        default=None,
        description="User-specific data if user is authenticated",
    )


# ===== Response Type Aliases =====

TitleDetailResponse = BaseContentResponse[TitleWithUserDataResponse]
TitleSearchResponse = PaginatedContentResponse[list[TitleWithUserDataResponse]]
