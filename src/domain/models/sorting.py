from enum import Enum

__all__ = ["SortingOrder", "TitleSortBy"]


class SortingOrder(str, Enum):
    ASC = "asc"
    DESC = "desc"


class TitleSortBy(str, Enum):
    ID = "id"
    RATING = "rating"
    POPULARITY = "popularity"
    CHAPTERS = "chapters"
    VIEWS = "views"
    FAVORITES = "favorites"
    RELEASED_AT = "released_at"
    UPDATED_AT = "updated_at"
