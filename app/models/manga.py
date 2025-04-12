from datetime import datetime, timezone
from sqlalchemy import Column, DateTime
from sqlmodel import Field, SQLModel
from sqlmodel import Enum as SQLEnum

from app.core import MC


# Base model for manga data
class MangaBase(SQLModel):
    id: str | None = Field(default=None, primary_key=True, index=True)
    source_id: str
    source_name: str
    name: str
    slug: str
    alt_names: str
    description: str
    avg_rating: str
    views: int
    chapters: int
    cover: str
    status: str
    translate_status: str
    year: int = Field(ge=1900)
    genres: str
    categories: str
    last_update: datetime = Field(
        sa_column=Column(DateTime(timezone=True), nullable=False),
        default_factory=lambda: datetime.now(timezone.utc),
    )

# Model for user's manga with reading progress and section data
class UserMangaWithData(MangaBase):
    current_url: str
    section: MC.Section = Field(sa_column=SQLEnum(MC.Section))
    last_read: datetime


# Model for storing manga information
class Manga(MangaBase, table=True): ...