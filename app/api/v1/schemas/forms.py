from pydantic import BaseModel, Field

from app.infrastructure.db.models import *

class GenresForm(BaseModel):
    genres: list[Genre] = Field(default=[])

class TypesForm(BaseModel):
    types: list[str] = Field(default=[])

class StatusesForm(BaseModel):
    statuses: list[str] = Field(default=[])

class BookMarksForm(BaseModel):
    bookmarks: list[str] = Field(default=[])