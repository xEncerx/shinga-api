from pydantic import BaseModel, Field, EmailStr
from datetime import datetime, timezone
from typing import Any

from app.infrastructure.db.models.user.relations import *
from app.core import settings


class UserSignUp(BaseModel):
    username: str = Field(..., min_length=3, max_length=20)
    email: EmailStr = Field(..., max_length=255)
    password: str = Field(..., min_length=8, max_length=128)


class ForgotPasswordForm(BaseModel):
    email: EmailStr = Field(..., max_length=255)


class UserPasswordRestore(BaseModel):
    email: EmailStr = Field(..., max_length=255)
    code: str = Field(..., min_length=6, max_length=6)
    new_password: str = Field(..., min_length=8, max_length=128)


class UserPublic(BaseModel):
    username: str
    email: EmailStr

    is_staff: bool = Field(default=False)
    is_superuser: bool = Field(default=False)

    avatar: str = settings.DEFAULT_AVATAR_PATH

    avg_rating: float = Field(default=0.0, ge=0.0, le=10.0)
    count_likes: int = Field(default=0, ge=0)
    count_votes: int = Field(default=0, ge=0)
    count_comments: int = Field(default=0, ge=0)
    count_bookmarks: BookMarksCount = Field(default=BookMarksCount())
    description: str | None = Field(default=None, max_length=1000)

    extra_data: dict[str, Any] | None = Field(default=None)


class UserTitlePublic(BaseModel):
    username: str
    title_id: str

    user_rating: int = Field(default=0, ge=0, le=10)
    current_url: str | None = Field(default=None)
    bookmark: str = Field(default=BookMarkType.NOT_READING)

    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
    )


class UserUpdatableFields(BaseModel):
    username: str | None = Field(default=None, min_length=3, max_length=20)
    avatar: str | None = Field(default=None)
    description: str | None = Field(default=None, max_length=1000)


class UserTitleUpdatableFields(BaseModel):
    title_id: str

    user_rating: int = Field(default=0, ge=0, le=10)
    current_url: str | None = Field(default=None)
    bookmark: BookMarkType = Field(default=BookMarkType.NOT_READING)


class GetUserTitlesFields(BaseModel):
    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=10, ge=1, le=100)
    bookmark: BookMarkType | None = Field(default=None)
