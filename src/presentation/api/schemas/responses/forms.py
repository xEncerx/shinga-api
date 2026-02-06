from typing import Generic, TypeVar
from pydantic import BaseModel, Field

T = TypeVar("T")

__all__ = [
    "TitleGenresResponse",
    "TitleCategoriesResponse",
    "TitleStatusesResponse",
    "TitleTypesResponse",
    "TitleGenreForm",
    "TitleCategoryForm",
    "TitleStatusForm",
    "TitleTypeForm",
]


class FormsResponse(BaseModel, Generic[T]):
    """ """

    content: list[T] = Field(
        ...,
        description="Forms content with dynamic values (genres, statuses, categories, etc.)",
    )


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


# ===== Response Type Aliases =====

TitleGenresResponse = FormsResponse[TitleGenreForm]
TitleCategoriesResponse = FormsResponse[TitleCategoryForm]
TitleStatusesResponse = FormsResponse[TitleStatusForm]
TitleTypesResponse = FormsResponse[TitleTypeForm]
