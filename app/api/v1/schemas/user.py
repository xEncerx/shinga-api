from pydantic import BaseModel, Field, EmailStr
from typing import Any

from app.infrastructure.db.models.user.relations import BookMarksCount
from app.core import settings

class UserIn(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr = Field(..., max_length=255)
    password: str = Field(..., min_length=8, max_length=128)

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