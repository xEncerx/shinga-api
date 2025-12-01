from sqlmodel import SQLModel, Field, Column, DateTime, func, Index
from sqlalchemy.dialects.postgresql import TSVECTOR, JSONB, ARRAY
from datetime import datetime, timezone
from sqlmodel import Enum as SQLEnum
from typing import Any

from ...sql_types import JSONBWithModel
from app.domain.enums import *
from .relations import *


class Title(SQLModel, table=True):
    __tablename__ = "titles"  # type: ignore

    id: int | None = Field(default=None, primary_key=True, index=True)
    cover: TitleCover = Field(sa_type=JSONBWithModel(TitleCover))  # type: ignore
    name_en: str | None = Field(default=None)
    name_ru: str | None = Field(default=None)
    alt_names: list[str] = Field(default=[], sa_type=JSONB)
    type_: TitleType = Field(
        sa_column=Column(
            SQLEnum(TitleType),
            nullable=False,
            index=True,
        ),
    )  # type: ignore
    chapters: int = Field(default=0, index=True)
    volumes: int = Field(default=0)
    views: int = Field(default=0, index=True)

    # In app rating
    in_app_rating: float | None = Field(default=0, ge=0, le=10)
    in_app_scored_by: int | None = Field(default=0)

    status: TitleStatus = Field(
        sa_column=Column(
            SQLEnum(TitleStatus),
            nullable=False,
            index=True,
        ),
    )  # type: ignore
    date: TitleReleaseTime = Field(sa_type=JSONBWithModel(TitleReleaseTime))  # type: ignore
    # Mal or other providers rating
    rating: float = Field(ge=0, le=10, index=True)

    scored_by: int = Field(default=0, index=True)
    popularity: int = Field(default=0, index=True)
    favorites: int = Field(default=0)
    description: TitleDescription = Field(sa_type=JSONBWithModel(TitleDescription))  # type: ignore
    authors: list[str] = Field(default=[], sa_type=JSONB)
    genres: list[TitleGenre] = Field(
        sa_column=Column(
            ARRAY(SQLEnum(TitleGenre)),
            nullable=True,
            index=True,
        ),
    )  # type: ignore

    # Timestamps for creation and last update
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
    )

    # A score indicating the quality of the data for this title (e.g., completeness, accuracy)
    data_quality_score: float = Field(default=0.0)

    # The primary source provider for this title
    primary_source: SourceProvider | None = Field(default=None, sa_column=SQLEnum(SourceProvider))  # type: ignore

    # This field is used to store additional data that may not fit into the predefined fields.
    extra_data: dict[str, Any] = Field(default={}, sa_type=JSONB)

    # Full-text search vector for efficient searching
    search_vector: str | None = Field(default=None, sa_type=TSVECTOR)

    __table_args__ = (
        Index(
            "idx_title_search_vector",
            "search_vector",
            postgresql_using="gin",
        ),
        Index(
            "idx_title_name_ru_trigram",
            "name_ru",
            postgresql_using="gin",
            postgresql_ops={"name_ru": "gin_trgm_ops"},
        ),
        Index(
            "idx_title_name_en_trigram",
            "name_en",
            postgresql_using="gin",
            postgresql_ops={"name_en": "gin_trgm_ops"},
        ),
        Index(
            "idx_title_alt_names_gin",
            "alt_names",
            postgresql_using="gin",
        ),
        Index(
            "idx_title_type_status",
            "type_",
            "status",
        ),
        # Составной индекс для сортировки по рейтингу
        Index(
            "idx_title_rating_scored_by",
            "rating",
            "scored_by",
        ),
        # Составной индекс для фильтрации и сортировки
        Index(
            "idx_title_type_status_rating",
            "type_",
            "status",
            "rating",
        ),
        # GIN индекс для extra_data
        Index(
            "idx_title_extra_data_gin",
            "extra_data",
            postgresql_using="gin",
        ),
    )
