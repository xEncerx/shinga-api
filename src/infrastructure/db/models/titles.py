from sqlmodel import SQLModel, Field, Column, func, DateTime, Index, text
from sqlalchemy.dialects.postgresql import JSONB, ARRAY, TSVECTOR
from sqlalchemy import Enum as SQLEnum

from datetime import datetime, timezone

from src.infrastructure.db.types import PydanticJsonType
from src.domain.models.titles.relations import *
from src.domain.models.source import Source


class TitleDBModel(SQLModel, table=True):
    __tablename__ = "titles"  # type: ignore

    id: int | None = Field(default=None, primary_key=True, index=True)

    # === Matching metadata ===
    mal_id: int | None = Field(
        default=None,
        unique=True,
        index=True,
        description="MyAnimeList ID (if known) - used for definitive matching",
    )

    search_text: str = Field(
        index=True,
        description="Normalized search text: TextNormalizer.normalize_multiple([name_ru, name_en, *alt_names])",
    )

    # === Title names ===
    name_ru: str | None = Field(default=None)
    name_en: str | None = Field(default=None)
    alt_names: list[str] = Field(default=[], sa_type=JSONB)

    # === Title descriptions ===
    description_ru: str | None = Field(default=None)
    description_en: str | None = Field(default=None)

    # === Title statistics ===
    popularity: int = Field(default=0, ge=0, index=True)
    rating: float = Field(default=0.0, ge=0.0, le=10.0, index=True)
    scored_by: int = Field(default=0, ge=0)
    chapters: int = Field(default=0, ge=0, index=True)
    volumes: int = Field(default=0, ge=0)
    views: int = Field(default=0, ge=0, index=True)
    favorites: int = Field(default=0, ge=0, index=True)

    # === Title themes ===
    genres: list[TitleGenre] = Field(
        sa_column=Column(
            ARRAY(SQLEnum(TitleGenre)),
            default=[],
            index=True,
        )
    )
    categories: list[TitleCategory] = Field(
        sa_column=Column(
            ARRAY(SQLEnum(TitleCategory)),
            default=[],
            index=True,
        )
    )

    # === Title authors ===
    authors: list[str] = Field(
        default=[],
        sa_type=JSONB,
        description="List of authors of the title",
    )

    # === Title cover ===
    cover: TitleCover = Field(
        sa_column=Column(
            PydanticJsonType(TitleCover),
        ),
        description="Path to the cover image of the title in the storage",
    )

    # === Title date information ===
    released_at: datetime | None = Field(
        sa_column=Column(DateTime(timezone=True), nullable=True, index=True),
        default=None,
    )
    ended_at: datetime | None = Field(
        sa_column=Column(DateTime(timezone=True), nullable=True, index=True),
        default=None,
    )

    type: TitleType = Field(
        sa_column=Column(
            SQLEnum(TitleType),
            nullable=False,
            index=True,
        ),
    )
    status: TitleStatus = Field(
        sa_column=Column(
            SQLEnum(TitleStatus),
            nullable=False,
            index=True,
        ),
    )

    # === Timestamps ===
    created_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            server_default=func.now(),
        ),
        default_factory=lambda: datetime.now(timezone.utc),
    )
    updated_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            server_default=func.now(),
            onupdate=func.now(),
        ),
        default_factory=lambda: datetime.now(timezone.utc),
        description="Last time master title was updated (merge/consolidation)",
    )

    # === Additional data ===
    data_quality_score: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        index=True,
        description="Quality score: 0.0-1.0 based on field completeness",
    )
    primary_source: Source = Field(
        sa_column=Column(
            SQLEnum(Source),
            nullable=False,
        ),
        description="Source from which title was initially created",
    )
    is_manual: bool = Field(
        default=False,
        index=True,
        description="True if title was manually created via CUSTOM source",
    )
    is_deleted: bool = Field(
        default=False,
        index=True,
        description="Indicates whether the title was marked as deleted",
    )

    extended_data: dict | None = Field(
        default=None,
        sa_column=Column(
            JSONB,
            nullable=True,
        ),
        description="Additional data from the source that doesn't fit into predefined fields",
    )

    # === Search Vector ===
    search_vector: str | None = Field(
        default=None,
        sa_type=TSVECTOR,
        description="Full-text search vector (auto-generated from search_text) by triggers in the database",
    )

    __table_args__ = (
        # GIN index for full-text search
        Index(
            "ix_titles_search_vector_gin",
            "search_vector",
            postgresql_using="gin",
        ),
        # Partial composite index for search COUNT: type + rating (only active titles)
        Index(
            "ix_titles_type_rating",
            "type",
            text("rating DESC"),
            postgresql_where=text("is_deleted = FALSE"),
        ),
        # Partial composite index for search COUNT: status + type + rating (only active titles)
        Index(
            "ix_titles_status_type_rating",
            "status",
            "type",
            text("rating DESC"),
            postgresql_where=text("is_deleted = FALSE"),
        ),
        # GIN index for trigram similarity search on search_text
        Index(
            "ix_titles_search_text_trgm",
            "search_text",
            postgresql_using="gin",
            postgresql_ops={"search_text": "gin_trgm_ops"},
        ),
        # Composite index for matching by type + released_at
        Index(
            "ix_titles_type_released",
            "type",
            "released_at",
        ),
        # Composite index for sorting/filtering
        Index(
            "ix_titles_rating_popularity",
            "rating",
            "popularity",
        ),
        # GIN index for genres array (for filtering by multiple genres)
        Index(
            "ix_titles_genres_gin",
            "genres",
            postgresql_using="gin",
        ),
        # GIN index for categories array
        Index(
            "ix_titles_categories_gin",
            "categories",
            postgresql_using="gin",
        ),
        # Composite index for status + type filtering
        Index(
            "ix_titles_status_type",
            "status",
            "type",
        ),
    )
