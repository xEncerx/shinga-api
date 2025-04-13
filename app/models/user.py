from datetime import datetime, timezone
from sqlalchemy import Column, DateTime
from sqlmodel import Field, SQLModel
from sqlmodel import Enum as SQLEnum

from app.core import MC


# Base model for user data transfer (without sensitive information)
class UserBase(SQLModel):
    username: str = Field(
        unique=True,
        primary_key=True,
        index=True,
        max_length=50,
    )


# Model for storing user information
class User(UserBase, table=True):
    hashed_password: str
    recovery_code: str | None
    registration_date: datetime = Field(
        sa_column=Column(DateTime(timezone=True), nullable=False),
        default_factory=lambda: datetime.now(timezone.utc),
    )


# Junction table for user-manga relationship with additional metadata
class UserManga(SQLModel, table=True):
    id: int | None = Field(
        default=None,
        primary_key=True,
        sa_column_kwargs={"autoincrement": True},
    )
    username: str = Field(foreign_key="user.username", index=True)
    manga_id: str = Field(foreign_key="manga.id", index=True)
    current_url: str
    section: MC.Section = Field(sa_column=SQLEnum(MC.Section))
    last_read: datetime = Field(
        sa_column=Column(DateTime(timezone=True), nullable=False),
        default_factory=lambda: datetime.now(timezone.utc),
    )
