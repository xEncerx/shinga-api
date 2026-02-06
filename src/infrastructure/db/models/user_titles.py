from sqlmodel import SQLModel, Field, Column, func, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime, timezone
from sqlalchemy import Enum as SQLEnum

from src.domain.models.titles import TitleBookmark

__all__ = ["UserTitlesDBModel"]


class UserTitlesDBModel(SQLModel, table=True):
    __tablename__ = "user_titles"  # type: ignore

    user_id: int = Field(foreign_key="users.id", index=True, primary_key=True)
    title_id: int = Field(foreign_key="titles.id", index=True, primary_key=True)

    rating: float = Field(
        default=0.0,
        ge=0.0,
        le=10.0,
        index=True,
    )
    current_url: str | None = Field(default=None)
    bookmark: TitleBookmark = Field(
        default=TitleBookmark.NOT_READING,
        sa_column=Column(
            SQLEnum(TitleBookmark),
            index=True,
        ),
    )

    is_favorite: bool = Field(default=False, index=True)

    updated_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            server_default=func.now(),
            onupdate=func.now(),
        ),
        default_factory=lambda: datetime.now(timezone.utc),
    )

    extended_data: dict | None = Field(
        default=None,
        sa_column=Column(
            JSONB,
            nullable=True,
        ),
        description="Additional data from the source that doesn't fit into predefined fields",
    )
