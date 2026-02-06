from enum import Enum

__all__ = ["Source"]


class Source(str, Enum):
    MAL = "MYANIMELIST"
    SHIKIMORI = "SHIKIMORI"
    REMANGA = "REMANGA"
    ANILIST = "ANILIST"
    CUSTOM = "CUSTOM"