from sqlmodel import Field, SQLModel
from enum import Enum

class BookMarkType(str, Enum):
    NOT_READING = "not reading"
    READING = "reading"
    COMPLETED = "completed"
    DROPPED = "dropped"
    PLANNED = "planned"

class BookMarksCount(SQLModel):
    total: int = Field(default=0)
    # * Count of bookmarks for each type of BookMarkType
    not_reading: int = Field(default=0)
    reading: int = Field(default=0)
    completed: int = Field(default=0)
    dropped: int = Field(default=0)
    planned: int = Field(default=0)

class UserVotes(SQLModel):
    total: int = Field(default=0)
    vote_1: int = Field(default=0)
    vote_2: int = Field(default=0)
    vote_3: int = Field(default=0)
    vote_4: int = Field(default=0)
    vote_5: int = Field(default=0)
    vote_6: int = Field(default=0)
    vote_7: int = Field(default=0)
    vote_8: int = Field(default=0)
    vote_9: int = Field(default=0)
    vote_10: int = Field(default=0)
