from app.domain.enums import TitleType, TitleStatus, TitleGenre, SourceProvider

from pydantic import BaseModel, Field, model_validator
from typing import Any


class TitleCoverData(BaseModel):
    """Cover image URLs"""

    url: str | None = None
    small_url: str | None = None
    large_url: str | None = None


class TitleDescriptionData(BaseModel):
    """Title description in multiple languages"""

    en: str | None = None
    ru: str | None = None


class TitleReleaseDateData(BaseModel):
    """Release date range"""

    from_: str | None
    to: str | None = None

    class Config:
        populate_by_name = True


class TitleData(BaseModel):
    """
    Standardized title data model for parsed data.

    This model serves as an intermediate representation between
    raw API responses and database models.
    """

    # === Identifiers ===
    source_provider: SourceProvider = Field(
        ...,
        description="Source provider (MAL, Remanga, Shikimori, etc.)",
    )
    source_id: str = Field(..., description="Unique ID from source provider")
    source_url: str | None = Field(None, description="URL on source website")

    # External IDs for matching
    mal_id: int | None = Field(
        default=None,
        description="MyAnimeList ID (critical for matching!)",
    )

    # === Basic Info ===
    cover: TitleCoverData
    name_en: str | None = Field(None, description="English title name")
    name_ru: str | None = Field(None, description="Russian title name")
    alt_names: list[str] = Field(
        default_factory=list,
        description="Alternative names/synonyms",
    )
    type_: TitleType = Field(
        ...,
        description="Title type (manga, manhwa, manhua, etc.)",
    )
    status: TitleStatus = Field(..., description="Publication status")

    # === Content Info ===
    chapters: int = Field(default=0, ge=0, description="Number of chapters")
    volumes: int = Field(default=0, ge=0, description="Number of volumes")
    date: TitleReleaseDateData | None = Field(None, description="Release date range")
    description: TitleDescriptionData | None = Field(
        None, description="Title description"
    )
    authors: list[str] = Field(default_factory=list, description="Author names")
    genres: list[TitleGenre] = Field(default_factory=list, description="Genre tags")
    views: int = Field(default=0, ge=0, description="Number of views")

    # === Statistics ===
    rating: float = Field(
        default=0.0,
        ge=0.0,
        le=10.0,
        description="Average rating (0-10)",
    )
    scored_by: int = Field(default=0, ge=0, description="Number of users who rated")
    popularity: int = Field(default=0, ge=0, description="Popularity rank")
    favorites: int = Field(default=0, ge=0, description="Number of favorites")

    # === Metadata ===
    extra_data: dict[str, Any] = Field(
        default_factory=dict, description="Additional provider-specific data"
    )

    class Config:
        populate_by_name = True
        use_enum_values = False
        json_encoders = {
            TitleType: lambda v: v.value,
            TitleStatus: lambda v: v.value,
            TitleGenre: lambda v: v.value,
            SourceProvider: lambda v: v.value,
        }

    @model_validator(mode="after")
    def validate_at_least_one_name(self) -> "TitleData":
        """Ensure at least one name is provided"""
        if not self.name_en and not self.name_ru:
            raise ValueError("At least one of name_en or name_ru must be provided")
        return self

    def to_raw_dict(self) -> dict[str, Any]:
        """
        Convert to dictionary for storing in TitleSourceData.raw_data

        Returns:
            Dictionary with all data serialized for JSON storage
        """
        data = self.model_dump(mode="json", by_alias=True, exclude_none=False)

        if self.genres:
            data["genres"] = [genre.name for genre in self.genres]

        return data

    def to_title_dict(self) -> dict[str, Any]:
        """
        Convert to dictionary suitable for Title model creation

        Returns:
            Dictionary matching Title model structure
        """
        return {
            "cover": self.cover if self.cover else None,
            "name_en": self.name_en,
            "name_ru": self.name_ru,
            "alt_names": self.alt_names,
            "type_": self.type_,
            "status": self.status,
            "chapters": self.chapters,
            "volumes": self.volumes,
            "date": self.date if self.date else None,
            "description": self.description if self.description else None,
            "authors": self.authors,
            "genres": self.genres,
            "rating": self.rating,
            "scored_by": self.scored_by,
            "popularity": self.popularity,
            "favorites": self.favorites,
            "primary_source": self.source_provider,
        }

    @classmethod
    def from_raw_dict(cls, data: dict[str, Any]) -> "TitleData":
        """
        Create TitleData from raw dictionary (e.g., from TitleSourceData.raw_data)

        Args:
            data: Raw dictionary from database

        Returns:
            TitleData instance
        """
        data = data.copy()

        if data.get("genres"):
            data["genres"] = [TitleGenre[genre] for genre in data["genres"]]

        return cls.model_validate(data)

    def get_all_names(self) -> list[str]:
        """Get all name variants for fuzzy matching"""
        names = []
        if self.name_en:
            names.append(self.name_en)
        if self.name_ru:
            names.append(self.name_ru)
        names.extend(self.alt_names)
        return names

    def __repr__(self) -> str:
        name = self.name_en or self.name_ru or "Unknown"
        return f"TitleData(source={self.source_provider.value}, id={self.source_id}, name='{name}')"
