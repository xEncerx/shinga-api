from sqlmodel import Field, Relationship, SQLModel
from datetime import datetime, timezone
from sqlmodel import Enum as SQLEnum
import uuid

from app.core import MC


# Base model for user data transfer (without sensitive information)
class UserBase(SQLModel):
    username: str = Field(unique=True, index=True, max_length=50)


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
class Users(UserBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str
    recovery_code: str | None
    registration_date: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
    )

    mangas: list["UsersManga"] = Relationship(back_populates="users")


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
        default_factory=lambda: datetime.now(timezone.utc),
    )


# Database model for storing manga information
class Mangas(MangaBase, table=True):
    users: list["UsersManga"] = Relationship(back_populates="mangas")


# Model for user's manga with reading progress and section data
class UserMangaWithData(MangaBase):
    current_url: str
    section: MC.Section = Field(sa_column=SQLEnum(MC.Section))
    last_read: datetime


# Response model for manga-related API endpoints
class MangaResponse(SQLModel):
    message: str = ""
    content: list[Mangas | UserMangaWithData | str | None]


# Junction table for user-manga relationship with additional metadata
class UsersManga(SQLModel, table=True):
    id: int | None = Field(
        default=None,
        primary_key=True,
        sa_column_kwargs={"autoincrement": True},
    )
    user_id: uuid.UUID = Field(foreign_key="users.id", index=True)
    manga_id: str = Field(foreign_key="mangas.id", index=True)
    current_url: str
    section: MC.Section = Field(sa_column=SQLEnum(MC.Section))
    last_read: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
    )

    users: Users = Relationship(back_populates="mangas")
    mangas: Mangas = Relationship(back_populates="users")


# Schema for updating user-manga relationship data
class UpdateUserManga(SQLModel):
    manga_id: str
    current_url: str = Field(default="")
    section: MC.Section = Field(sa_column=SQLEnum(MC.Section))
    last_read: datetime = Field(
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
