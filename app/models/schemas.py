from datetime import datetime, timezone
from sqlalchemy import Column, DateTime
from sqlmodel import Field, SQLModel
from sqlmodel import Enum as SQLEnum

from .manga import Manga, UserMangaWithData
from .user import UserBase

from app.core import MC


# Schema for updating user-manga relationship data
class UpdateUserManga(SQLModel):
    manga_id: str
    current_url: str = Field(default="")
    section: MC.Section = Field(sa_column=SQLEnum(MC.Section))
    last_read: datetime = Field(
        sa_column=Column(DateTime(timezone=True), nullable=False),
        default_factory=lambda: datetime.now(timezone.utc),
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


# Response model for manga-related API endpoints
class MangaResponse(SQLModel):
    message: str = ""
    content: list[Manga | UserMangaWithData | str | None]


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
