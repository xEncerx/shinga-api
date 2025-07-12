from sqlmodel import Field, SQLModel, Column, DateTime, func
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime, timezone
from sqlmodel import Enum as SQLEnum
from pydantic import EmailStr
from typing import Any

from ...sql_types import JSONBWithModel
from app.core import settings
from .relations import *

class User(SQLModel, table=True):
    __tablename__ = "users"  # type: ignore

    id: int | None = Field(default=None, primary_key=True, index=True)

    username: str = Field(index=True, unique=True, max_length=50)
    email: EmailStr = Field(unique=True, index=True, max_length=255)

    hashed_password: str

    # OAuth providers
    google_id: str | None = Field(default=None, index=True)
    yandex_id: str | None = Field(default=None, index=True)

    is_staff: bool = Field(default=False)
    is_superuser: bool = Field(default=False)

    avatar: str = settings.DEFAULT_AVATAR_PATH

    avg_rating: float = Field(default=0.0, ge=0, le=10)
    count_likes: int = Field(default=0)
    count_votes: int = Field(default=0)
    count_comments: int = Field(default=0)
    count_bookmarks: BookMarksCount = Field(default=BookMarksCount(), sa_type=JSONBWithModel(BookMarksCount)) # type: ignore
    description: str | None = Field(default=None, max_length=1000)

    extra_data: dict[str, Any] | None = Field(default=None, sa_type=JSONB)

    # Timestamps for registration
    registration_date: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True), nullable=False, server_default=func.now()
        ),
        default_factory=lambda: datetime.now(timezone.utc),
    )

class UserTitles(SQLModel, table=True):
    __tablename__ = "user_titles"  # type: ignore

    username: str = Field(foreign_key="users.username", index=True, primary_key=True)
    title_id: str = Field(foreign_key="titles.id", index=True, primary_key=True)

    user_rating: int = Field(ge=0, le=10)
    current_url: str | None
    bookmark: BookMarkType = Field(default=BookMarkType.NOT_READING, sa_column=SQLEnum(BookMarkType))  # type: ignore
    updated_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            server_default=func.now(),
            onupdate=func.now(),
        ),
        default_factory=lambda: datetime.now(timezone.utc),
    )

    extra_data: dict[str, Any] | None = Field(sa_type=JSONB)