from typing import Any

from app.utils.text import tag_remover
from app.core import MC


def status_validator(value: str | int) -> str:
    """
    Converts any status to one of the standard variants
    """
    value = str(value).lower().strip()

    for key, values in MC.STATUSES.items():
        if value in values:
            return key

    return MC.Status.UNKNOWN


def get_name(content: dict[str, Any], source_name: str) -> str:
    """Gets the main name of the manga."""
    match source_name:
        case MC.Sources.REMANGA:
            return content.get("main_name", "")
        case MC.Sources.SHIKIMORI:
            return content.get("russian") or content.get("name", "")
        case MC.Sources.MANGA_POISK:
            return content.get("name", "")


def get_slug(content: dict[str, Any], source_name: str) -> str:
    """Gets the slug (unique identifier)."""
    match source_name:
        case MC.Sources.REMANGA:
            return content.get("dir", "")
        case MC.Sources.SHIKIMORI:
            return str(content.get("id", ""))
        case MC.Sources.MANGA_POISK:
            return content.get("slug", "")


def get_alt_names(content: dict[str, Any], source_name: str) -> str:
    """Gets alternative names."""
    match source_name:
        case MC.Sources.REMANGA:
            return content.get("another_name") or content.get("secondary_name") or ""
        case MC.Sources.MANGA_POISK:
            return " / ".join(
                filter(
                    None,
                    [
                        content.get("name_alt"),
                        content.get("name_jp"),
                        content.get("name_en"),
                    ],
                )
            )
        case MC.Sources.SHIKIMORI:
            return " / ".join(
                filter(
                    None,
                    [
                        (
                            " / ".join(synonyms)
                            if (synonyms := content.get("synonyms"))
                            else None
                        ),
                        content.get("japanese"),
                        content.get("english"),
                    ],
                )
            )


def get_description(content: dict[str, Any]) -> str:
    """Cleans and gets the description."""
    description = content.get("description")
    return tag_remover(description) if description else "No description"


def get_rating(content: dict[str, Any], source_name: str) -> str:
    """Gets the rating."""
    match source_name:
        case MC.Sources.REMANGA:
            return str(content.get("avg_rating", -1))
        case MC.Sources.SHIKIMORI:
            return str(content.get("score", -1))
        case MC.Sources.MANGA_POISK:
            return str(content.get("rating", -0.5) * 2)


def get_views(content: dict[str, Any], source_name: str) -> int:
    """Gets the number of views."""
    match source_name:
        case MC.Sources.REMANGA:
            return content.get("total_views", -1)
        case MC.Sources.SHIKIMORI:
            return sum(i.get("count", 0) for i in content.get("statusesStats", []))
        case MC.Sources.MANGA_POISK:
            return -1


def get_chapters(content: dict[str, Any], source_name: str) -> int:
    """Gets the number of chapters."""
    match source_name:
        case MC.Sources.REMANGA:
            return content.get("count_chapters", -1)
        case MC.Sources.SHIKIMORI:
            return content.get("chapters", -1)
        case MC.Sources.MANGA_POISK:
            return content.get("chapters_count", -1)


def get_cover(content: dict[str, Any], source_name: str) -> str:
    """Gets the cover image."""
    match source_name:
        case MC.Sources.REMANGA:
            return (
                "https://remanga.org" + list(img.values())[-1]
                if (img := content.get("img", {}))
                else ""
            )
        case MC.Sources.SHIKIMORI:
            return content.get("poster", {}).get("originalUrl", "")
        case MC.Sources.MANGA_POISK:
            return content.get("poster", {}).get("link", "")


def get_status(content: dict[str, Any], source_name: str) -> str:
    """Gets the manga status."""
    status = ""

    match source_name:
        case MC.Sources.REMANGA:
            status = content.get("status", {}).get("name", MC.Status.UNKNOWN)
        case MC.Sources.SHIKIMORI:
            status = content.get("status", MC.Status.UNKNOWN)
        case MC.Sources.MANGA_POISK:
            status = content.get("translated", MC.Status.UNKNOWN)

    return status_validator(status)


def get_translate_status(content: dict[str, Any], source_name: str) -> str:
    """Gets the translation status."""
    status = ""

    match source_name:
        case MC.Sources.REMANGA:
            # Remanga quirk: in global search it gives status as a number
            # In normal search it's a dictionary with name and number
            # And also the same number means different statuses...
            status = (
                status.get("name", MC.Status.UNKNOWN)
                if isinstance((status := content.get("translate_status")), dict)
                else status
            )
        case MC.Sources.SHIKIMORI:
            status = content.get("status", MC.Status.UNKNOWN)
        case MC.Sources.MANGA_POISK:
            status = content.get("translated", MC.Status.UNKNOWN)

    return status_validator(status)


def get_year(content: dict[str, Any], source_name: str) -> int:
    """Gets the release year."""
    match source_name:
        case MC.Sources.REMANGA:
            return content.get("issue_year", -1)
        case MC.Sources.SHIKIMORI:
            return content.get("airedOn", {}).get("year", -1)
        case MC.Sources.MANGA_POISK:
            return content.get("year", -1)


def get_genres(content: dict[str, Any], source_name: str) -> str:
    """Gets the genres."""
    match source_name:
        case MC.Sources.REMANGA:
            return " / ".join(
                [i["name"] for i in genres]
                if (genres := content.get("genres", []))
                else []
            )

        case MC.Sources.SHIKIMORI:
            return " / ".join([i.get("russian", "") for i in content.get("genres", [])])
        case MC.Sources.MANGA_POISK:
            return " / ".join(
                [i.get("title", "") for i in genres]
                if (genres := content.get("genres", []))
                else []
            )


def get_categories(content: dict[str, Any], source_name: str) -> str:
    """Gets the categories."""
    match source_name:
        case MC.Sources.REMANGA:
            return " / ".join(
                [i["name"] for i in categories]
                if (categories := content.get("categories", []))
                else []
            )
        case MC.Sources.SHIKIMORI:
            return ""
        case MC.Sources.MANGA_POISK:
            return ""
