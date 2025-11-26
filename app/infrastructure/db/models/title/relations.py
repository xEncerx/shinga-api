from sqlmodel import SQLModel, Field

from app.core import settings


class TitleCover(SQLModel):
    url: str | None = Field(default=None)
    small_url: str | None = Field(default=None)
    large_url: str | None = Field(default=None)

    @staticmethod
    def error_placeholder() -> "TitleCover":
        return TitleCover(
            url=settings.COVER_404_PATH,
            small_url=settings.COVER_404_PATH,
            large_url=settings.COVER_404_PATH,
        )

    @staticmethod
    def pending_placeholder() -> "TitleCover":
        return TitleCover(
            url=settings.COVER_PENDING_PATH,
            small_url=settings.COVER_PENDING_PATH,
            large_url=settings.COVER_PENDING_PATH,
        )


class TitleReleaseTime(SQLModel):
    from_: str | None = Field(
        default=None, description="Release start date in ISO 8601 format"
    )
    to: str | None = Field(
        default=None, description="Release end date in ISO 8601 format, if applicable"
    )


class TitleDescription(SQLModel):
    en: str | None = Field(default=None)
    ru: str | None = Field(default=None)
