from pydantic import BaseModel, Field
from datetime import datetime
from typing import Any

from app.infrastructure.db.models import *
from app.domain.models import Pagination
from .user import UserTitlePublic


class TitlePublic(BaseModel):
    id: str

    name_en: str | None = Field(default=None)
    name_ru: str | None = Field(default=None)
    cover: TitleCover
    alt_names: list[str] = Field(default=[])
    type_: TitleType
    chapters: int = Field(default=0)
    volumes: int = Field(default=0)
    views: int = Field(default=0)

    in_app_rating: float | None = Field(default=0, ge=0, le=10)
    in_app_scored_by: int | None = Field(default=0)

    status: TitleStatus
    date: TitleReleaseTime
    rating: float = Field(ge=0, le=10)

    scored_by: int = Field(default=0)
    popularity: int = Field(default=0)
    favorites: int = Field(default=0)
    description: TitleDescription
    authors: list[str] = Field(default=[])
    genres: list[TitleGenre] = Field(default=[])

    updated_at: datetime
    extra_data: dict[str, Any] | None = Field(default=None)


class TitleWithUserData(BaseModel):
    title: TitlePublic
    user_data: UserTitlePublic | None = Field(default=None)


class TitleSearchResponse(BaseModel):
    message: str = Field(default="")
    content: list[TitleWithUserData] = Field(default=[])


class TitlePaginationResponse(BaseModel):
    message: str = Field(default="")
    pagination: Pagination
    content: list[TitleWithUserData] = Field(default=[])


class TitleSortBy(str, Enum):
    rating = "rating"
    popularity = "popularity"
    favorites = "favorites"
    chapters = "chapters"
    views = "views"
    user_updated_at = "user_updated_at"


class TitleSortOrder(str, Enum):
    asc = "asc"
    desc = "desc"


class TitleSearchFields(BaseModel):
    query: str | None = Field(default=None)
    genres: list[str] | None = Field(default=None)
    status: list[TitleStatus] | None = Field(default=None)
    type_: list[TitleType] | None = Field(default=None)
    min_rating: float | None = Field(default=None, ge=0, le=10)
    max_rating: float | None = Field(default=None, ge=0, le=10)
    min_chapters: int | None = Field(default=None, ge=0)
    max_chapters: int | None = Field(default=None, ge=0)
    sort_by: TitleSortBy = Field(default=TitleSortBy.rating)
    sort_order: TitleSortOrder = Field(default=TitleSortOrder.desc)
    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=21, ge=1, le=50)
    bookmark: BookMarkType | None = Field(default=None)
