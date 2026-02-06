from pydantic import BaseModel, Field, HttpUrl

from src.domain.models.titles.relations import TitleBookmark

__all__ = ["AddUserTitleRequest", "UpdateUserTitleRequest"]


class AddUserTitleRequest(BaseModel):
    bookmark: TitleBookmark = Field(
        description="The bookmark status of the title for the user.",
    )


class UpdateUserTitleRequest(BaseModel):
    rating: float | None = Field(
        default=None,
        ge=0.0,
        le=10.0,
        description="The user's rating for the title, from 0.0 to 10.0.",
    )
    current_url: HttpUrl | None = Field(
        default=None,
        description="The current URL of the title for the user.",
    )
    bookmark: TitleBookmark | None = Field(
        default=None,
        description="The bookmark status of the title for the user.",
    )

    is_favorite: bool | None = Field(
        default=None,
        description="Indicates if the title is marked as a favorite by the user.",
    )
