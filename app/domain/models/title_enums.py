from enum import Enum


class TitleSortBy(str, Enum):
    rating = "rating"
    popularity = "popularity"
    favorites = "favorites"
    chapters = "chapters"
    views = "views"
    user_updated_at = "user_updated_at"


class TitleSortOrder(str, Enum):
    asc = "asc"
    desc = "desc"
