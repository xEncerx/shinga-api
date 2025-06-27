from sqlmodel import SQLModel, Field
from enum import Enum
from datetime import datetime

class TitleGenre(SQLModel):
    ru: str | None
    en: str | None


class TitleCover(SQLModel):
    url: str | None
    small_url: str | None
    large_url: str | None


class TitleType(str, Enum):
    MANGA = "manga"
    NOVEL = "novel"
    LIGHT_NOVEL = "lightnovel"
    ONESHOT = "one-shot"
    DOUJIN = "doujin"
    MANHWA = "manhwa"
    MANHUA = "manhua"
    WEBTOON = "webtoon"
    OTHER = "other"

class TitleReleaseTime(SQLModel):
    from_: datetime | None = Field(alias="from")
    to: datetime | None

    def __init__(self, from_: str, to: str | None = None):
        self.from_ = datetime.fromisoformat(from_) if from_ else None
        self.to = datetime.fromisoformat(to) if to else None

class TitleDescription(SQLModel):
    en: str | None
    ru: str | None

class TitleStatus(str, Enum):
    ONGOING = "publishing"
    FINISHED = "finished"
    DISCONTINUED = "discontinued"
    FROZEN = "on hiatus"
    ANONS = "upcoming"
    UNKNOWN = "unknown"