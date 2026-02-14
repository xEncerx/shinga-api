from pydantic import BaseModel, Field
from typing import TypeVar

from .base import BaseContentResponse

T = TypeVar("T")

__all__ = [
    "TitleGenresResponse",
    "TitleCategoriesResponse",
    "TitleStatusesResponse",
    "TitleTypesResponse",
    "TitleBookmarksResponse",
    "TitleGenreForm",
    "TitleCategoryForm",
    "TitleStatusForm",
    "TitleTypeForm",
    "TitleBookmarkForm",
]


class FormsResponse(BaseContentResponse[list[T]]):
    """Response for forms with list content."""


# ===== Form Models =====


class TitleGenreForm(BaseModel):
    """Genre form model"""

    name: str = Field(..., description="Genre name in System")
    ru: str = Field(..., description="Russian genre translation")
    en: str = Field(..., description="English genre translation")


class TitleCategoryForm(BaseModel):
    """Category form model"""

    name: str = Field(..., description="Category name in System")
    ru: str = Field(..., description="Russian category translation")
    en: str = Field(..., description="English category translation")


class TitleStatusForm(BaseModel):
    """Status form model"""

    name: str = Field(..., description="Status name in System")


class TitleTypeForm(BaseModel):
    """Type form model"""

    name: str = Field(..., description="Type name in System")


class TitleBookmarkForm(BaseModel):
    """Bookmark form model"""

    name: str = Field(..., description="Bookmark name in System")


# ===== Response Type Aliases =====

TitleGenresResponse = FormsResponse[TitleGenreForm]
TitleCategoriesResponse = FormsResponse[TitleCategoryForm]
TitleStatusesResponse = FormsResponse[TitleStatusForm]
TitleTypesResponse = FormsResponse[TitleTypeForm]
TitleBookmarksResponse = FormsResponse[TitleBookmarkForm]
