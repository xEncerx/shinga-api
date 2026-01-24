from enum import Enum

__all__ = ["Source"]


class Source(str, Enum):
    MAL = "mal"
    SHIKIMORI = "shikimori"
    REMANGA = "remanga"
    CUSTOM = "custom"
