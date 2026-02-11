from pydantic import BaseModel, Field, field_validator, field_serializer
from datetime import datetime

from src.domain.models.titles.relations import *

__all__ = ["TitleData"]


class TitleData(BaseModel):
    """Pure domain model representing title information without any source-specific details."""

    id: int | None = Field(default=None, description="Unique identifier for the title")
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
    genres: list[TitleGenre] = Field(
        default=[],
        description="List of genres associated with the title. Each genre includes names in Russian and English.",
    )
    categories: list[TitleCategory] = Field(
        default=[],
        description="List of categories associated with the title. Each category includes names in Russian and English.",
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
        description="Cover images of the title in various sizes. Each size includes a URL to the image.",
    )

    @field_validator("genres", mode="before")
    @classmethod
    def deserialize_genres(cls, values):
        if not values:
            return []
        result = []
        for v in values:
            if isinstance(v, str):
                result.append(TitleGenre[v])
            elif isinstance(v, TitleGenre):
                result.append(v)
        return result

    @field_validator("categories", mode="before")
    @classmethod
    def deserialize_categories(cls, values):
        if not values:
            return []
        result = []
        for v in values:
            if isinstance(v, str):
                result.append(TitleCategory[v])
            elif isinstance(v, TitleCategory):
                result.append(v)
        return result

    @field_serializer("genres", "categories")
    def serialize_enum_list(self, values: list, _info):
        return [v.name for v in values]
