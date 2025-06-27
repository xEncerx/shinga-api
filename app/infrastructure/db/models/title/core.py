from sqlmodel import SQLModel, Field, JSON
from sqlmodel import Enum as SQLEnum

from .relations import *


class Title(SQLModel, table=True):
    __tablename__ = "titles" # type: ignore

    id: int = Field(primary_key=True, index=True)
    cover: TitleCover = Field(sa_type=JSON)
    name_en: str
    name_ru: str
    alt_names: list[str] = Field(sa_type=JSON)
    type_: TitleType = Field(sa_column=SQLEnum(TitleType)) # type: ignore
    chapters: int
    volumes: int
    status: TitleStatus = Field(sa_column=SQLEnum(TitleStatus)) # type: ignore
    published: bool
    date: TitleReleaseTime = Field(sa_type=JSON)
    rating: float
    scored_by: int
    popularity: int
    favorites: int
    description: TitleDescription = Field(sa_type=JSON)
    authors: list[str] = Field(sa_type=JSON)
    genres: list[TitleGenre] = Field(sa_type=JSON)
