from sqlmodel import Field, Relationship, SQLModel
from datetime import datetime, timezone
from sqlalchemy import Column, DateTime
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


# Schema for user registration (includes password)
class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=40)


# Schema for updating user information
class UserUpdate(UserBase):
    username: str = Field(unique=True, index=True, max_length=50)
    password: str = Field(min_length=8, max_length=40)


# Schema for account recovery process
class UserRecoveryCode(UserBase):
    message: str | None
    recovery_code: str


# Schema for password change operation
class UpdatePassword(SQLModel):
    current_password: str = Field(min_length=8, max_length=40)
    new_password: str = Field(min_length=8, max_length=40)
    recovery_code: str


# Database model for storing user information
class User(UserBase, table=True):
    hashed_password: str
    recovery_code: str | None
    registration_date: datetime = Field(
        sa_column=Column(DateTime(timezone=True), nullable=False),
        default_factory=lambda: datetime.now(timezone.utc),
    )

    manga: list["UserManga"] = Relationship(back_populates="user")


# Base model for manga data
class MangaBase(SQLModel):
    id: str | None = Field(default=None, primary_key=True, index=True)
    source_id: str
    source_name: str
    name: str
    slug: str
    alt_names: str
    description: str
    avg_rating: str
    views: int
    chapters: int
    cover: str
    status: str
    translate_status: str
    year: int = Field(ge=1900)
    genres: str
    categories: str
    last_update: datetime = Field(
        sa_column=Column(DateTime(timezone=True), nullable=False),
        default_factory=lambda: datetime.now(timezone.utc),
    )


# Database model for storing manga information
class Manga(MangaBase, table=True):
    user: list["UserManga"] = Relationship(back_populates="manga")


# Model for user's manga with reading progress and section data
class UserMangaWithData(MangaBase):
    current_url: str
    section: MC.Section = Field(sa_column=SQLEnum(MC.Section))
    last_read: datetime


# Response model for manga-related API endpoints
class MangaResponse(SQLModel):
    message: str = ""
    content: list[Manga | UserMangaWithData | str | None]


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

    user: User = Relationship(back_populates="manga")
    manga: Manga = Relationship(back_populates="user")


# Schema for updating user-manga relationship data
class UpdateUserManga(SQLModel):
    manga_id: str
    current_url: str = Field(default="")
    section: MC.Section = Field(sa_column=SQLEnum(MC.Section))
    last_read: datetime = Field(
        sa_column=Column(DateTime(timezone=True), nullable=False),
        default_factory=lambda: datetime.now(timezone.utc),
    )


# JSON payload containing access token
class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


# Contents of JWT token
class TokenPayload(SQLModel):
    sub: str


# Generic message response model
class Message(SQLModel):
    message: str
