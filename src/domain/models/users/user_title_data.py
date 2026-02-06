from pydantic import BaseModel, Field

from src.domain.models.titles.relations import TitleBookmark

__all__ = ["UserTitleData", "UserTitleDataUpdate"]


class UserTitleData(BaseModel):
    rating: float = Field(
        default=0.0,
        ge=0.0,
        le=10.0,
        description="The user's rating for the title, from 0.0 to 10.0.",
    )
    current_url: str | None = Field(
        default=None,
        description="The current URL of the title for the user.",
    )
    bookmark: TitleBookmark = Field(
        default=TitleBookmark.NOT_READING,
        description="The bookmark status of the title for the user.",
    )

    # Fields for future use
    is_favorite: bool = Field(
        default=False,
        description="Indicates if the title is marked as a favorite by the user.",
    )

    extended_data: dict | None = Field(
        default=None,
        description="Additional specific data that doesn't fit into predefined fields",
    )


class UserTitleDataUpdate(BaseModel):
    rating: float | None = None
    bookmark: TitleBookmark | None = None
    current_url: str | None = None
    is_favorite: bool | None = None
    extended_data: dict | None = None
