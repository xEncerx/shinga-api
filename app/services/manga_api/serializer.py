from typing import Any, Callable, TypeVar
from functools import wraps

from app.models import Manga, MangaResponse
from app.utils.manga_parsers import *
from app.utils import logger
from app.core import MC


T = TypeVar("T")


def handle_empty_data(default_return: Any = []):
    """Decorator that handles empty data for serializers"""

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(data: dict, *args, **kwargs):
            if not data:
                return default_return
            return func(data, *args, **kwargs)

        return wrapper

    return decorator


def base_serializer(
    content: dict[str, str | int],
    source_name: str,
) -> Manga:
    """
    Basic serializer with common data transformation logic.
    """

    try:
        return Manga(
            id=f"{source_name}|{content.get('id', '')}",
            source_id=str(content.get("id", "")),
            source_name=source_name,
            name=get_name(content, source_name),
            slug=get_slug(content, source_name),
            alt_names=get_alt_names(content, source_name),
            description=get_description(content),
            avg_rating=get_rating(content, source_name),
            views=get_views(content, source_name),
            chapters=get_chapters(content, source_name),
            cover=get_cover(content, source_name),
            status=get_status(content, source_name),
            translate_status=get_translate_status(content, source_name),
            year=get_year(content, source_name),
            genres=get_genres(content, source_name),
            categories=get_categories(content, source_name),
        )
    except Exception as e:
        logger.error(f"Serialization error: {e}")
        return None


@handle_empty_data()
def remanga_serializer(data: list[dict] | dict) -> list[Manga]:
    return _serialize_list(data["content"], MC.Sources.REMANGA)


@handle_empty_data()
def shikimori_serializer(data: list[dict] | dict) -> list[Manga]:
    return _serialize_list(data["data"]["mangas"], MC.Sources.SHIKIMORI)


@handle_empty_data()
def manga_poisk_serializer(data: list[dict] | dict) -> list[Manga]:
    return _serialize_list(data["props"]["manga"]["data"], MC.Sources.MANGA_POISK)


def _serialize_list(
    data: list[dict] | dict,
    source_name: str,
) -> list[Manga]:
    if not data:
        return []

    if isinstance(data, dict):
        data = [data]

    return [base_serializer(item, source_name) for item in data if item]
