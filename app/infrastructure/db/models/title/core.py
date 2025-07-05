from sqlmodel import SQLModel, Field, Column, DateTime, func
from sqlalchemy.dialects.postgresql import TSVECTOR, JSONB
from datetime import datetime, timezone
from sqlmodel import Enum as SQLEnum
from typing import Any

from ...sql_types import JSONBWithModel
from .relations import *


class Title(SQLModel, table=True):
    __tablename__ = "titles"  # type: ignore

    id: str = Field(primary_key=True, index=True)
    cover: TitleCover = Field(sa_type=JSONBWithModel(TitleCover)) # type: ignore
    name_en: str
    name_ru: str | None
    alt_names: list[str] = Field(sa_type=JSONB)
    type_: TitleType = Field(sa_column=SQLEnum(TitleType))  # type: ignore
    chapters: int
    volumes: int
    views: int = Field(default=0)

    # In app rating
    in_app_rating: float | None = Field(default=0, ge=0, le=10)
    in_app_scored_by: int | None = Field(default=0)

    status: TitleStatus = Field(sa_column=SQLEnum(TitleStatus))  # type: ignore
    date: TitleReleaseTime = Field(sa_type=JSONBWithModel(TitleReleaseTime)) # type: ignore
    # Mal or other providers rating
    rating: float = Field(ge=0, le=10)

    scored_by: int
    popularity: int
    favorites: int
    description: TitleDescription = Field(sa_type=JSONBWithModel(TitleDescription))  # type: ignore
    authors: list[str] = Field(sa_type=JSONB)
    genres: list[TitleGenre] = Field(sa_type=JSONBWithModel(TitleGenre), index=True) # type: ignore

    # Timestamps for creation and last update
    created_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True), nullable=False, server_default=func.now()
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

    # Source provider from which the title was fetched
    source_provider: SourceProvider = Field(
        default=SourceProvider.MAL,
        sa_column=SQLEnum(SourceProvider),  # type: ignore
    )
    # ID from the source provider
    source_id: str | None = None

    # This field is used to store additional data that may not fit into the predefined fields.
    extra_data: dict[str, Any] | None = Field(default=None, sa_type=JSONB)

    # Full-text search vector for efficient searching
    search_vector: str | None = Field(
        default=None, sa_type=TSVECTOR, sa_column_kwargs={"index": True}
    )
