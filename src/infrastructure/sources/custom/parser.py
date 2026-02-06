from src.core import logger
from ..base_parser import *


class CustomParser(BaseParser):
    @staticmethod
    def parse_title(data: dict) -> SourceTitleData:
        """
        Parse a single title from API response into SourceTitleData structure.
        """
        # Create source metadata
        source_metadata = SourceMetadata(
            source=Source.CUSTOM,
            external_id=str(data["id"]),
            source_url=data.get("url"),
        )

        # Create title data with available fields
        title_data = TitleData(
            # * Remove any fields that are not provided by your source
            mal_id=data.get("mal_id"),
            name_ru=data["name_ru"],
            name_en=data["name_en"],
            # * Use tag_remover utility to clean HTML tags from descriptions
            description_ru=tag_remover(data["description_ru"]),
            description_en=tag_remover(data["description_en"]),
            type=CustomParser.convert_type(data["type"]),
            status=CustomParser.convert_status(data["status"]),
            popularity=data["popularity"] or 0,
            chapters=data["chapters"] or 0,
            views=data["views"] or 0,
            volumes=data["volumes"] or 0,
            favorites=data["favorites"] or 0,
            rating=data["rating"] or 0.0,
            scored_by=data["scored_by"] or 0,
            # ! Timestamps must be converted to datetime format (timezone-naive).
            # The release/end year is mandatory. Other date components are optional.
            # If your source doesn't provide year data, omit these fields.
            released_at=(
                datetime.fromisoformat(x).replace(tzinfo=None)
                if (x := data["published"]["from"])
                else None
            ),
            ended_at=(
                datetime.fromisoformat(x).replace(tzinfo=None)
                if (x := data["published"]["to"])
                else None
            ),
            # Genres and categories are converted using mapping dictionaries below
            genres=[
                genre
                for genre_name in data["genres"]
                if (genre := CustomParser.convert_genre(genre_name["name"]))
            ],
            categories=[
                category
                for category_name in data["categories"]
                if (category := CustomParser.convert_category(category_name["name"]))
            ],
            # Authors and alternative names are optional
            authors=[author["name"] for author in data["authors"]],
            alt_names=data["title_synonyms"],
            # ! Cover URL (select the highest resolution available)
            # The system will automatically process and resize images as needed
            cover=TitleCover(
                thumbnail=data["images"]["small"],
                original=data["images"]["large"],
            ),
        )

        # Combine into final structure
        return SourceTitleData(
            source_metadata=source_metadata,
            title_data=title_data,
        )

    @staticmethod
    def parse_page(data: dict) -> list[SourceTitleData]:
        """
        Parse a catalog page from API response.

        Returns a list of SourceTitleData objects.
        Skips items that fail to parse and logs errors without interrupting the process.
        """
        parsed_titles = []
        for item in data["data"]:
            try:
                parsed_titles.append(CustomParser.parse_title(item))
            except (ValueError, KeyError) as e:
                logger.error(
                    f"Skipping Custom title id={item['id']}: {e}", exc_info=True
                )
                continue
            except Exception as e:
                logger.error(
                    f"Unexpected error parsing Custom title id={item['id']}: {e}",
                    exc_info=True,
                )
                continue

        return parsed_titles

    # === Converters ===
    @staticmethod
    def convert_type(data: str) -> TitleType:
        return CustomParser._TYPE_MAPPING.get(data.lower(), TitleType.OTHER)

    @staticmethod
    def convert_status(data: str) -> TitleStatus:
        return CustomParser._STATUS_MAPPING.get(data.lower(), TitleStatus.UNKNOWN)

    @staticmethod
    def convert_genre(data: str) -> TitleGenre | None:
        return CustomParser._GENRE_MAPPING.get(data)

    @staticmethod
    def convert_category(data: str) -> TitleCategory | None:
        return CustomParser._CATEGORY_MAPPING.get(data)

    # === Mapping Dictionaries ===
    # Map your source's values to standardized enums
    _GENRE_MAPPING: dict[str, TitleGenre] = {
        # Example: "Action": TitleGenre.ACTION,
    }

    _CATEGORY_MAPPING: dict[str, TitleCategory] = {
        # Example: "Anime": TitleCategory.ANIME
    }

    _TYPE_MAPPING: dict[str, TitleType] = {
        # Example: "manga": TitleType.MANGA,
    }

    _STATUS_MAPPING: dict[str, TitleStatus] = {
        # Example: "publishing": TitleStatus.ONGOING,
    }
