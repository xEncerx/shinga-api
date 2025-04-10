from app.utils.manga_parsers import *
from app.models import Mangas
from app.utils import logger
from app.core import MC


def base_serializer(
    content: dict[str, str | int],
    source_name: str,
) -> Mangas:
    """
    Basic serializer with common data transformation logic.
    """

    try:
        return Mangas(
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


def remanga_serializer(data: list[dict] | dict) -> list[Mangas]:
    return _serialize_list(data["content"], MC.Sources.REMANGA)


def shikimori_serializer(data: list[dict] | dict) -> list[Mangas]:
    return _serialize_list(data["data"]["mangas"], MC.Sources.SHIKIMORI)


def _serialize_list(
    data: list[dict] | dict,
    source_name: str,
) -> list[Mangas]:
    if not data:
        return []

    if isinstance(data, dict):
        data = [data]

    return [base_serializer(item, source_name) for item in data if item]
