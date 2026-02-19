from src.core import logger
from ..base_parser import *


class MalParser(BaseParser):
    @staticmethod
    def parse_title(data: dict) -> SourceTitleData:
        external_id = data["mal_id"]

        source_metadata = SourceMetadata(
            source=Source.MAL,
            external_id=str(external_id),
            source_url=data.get("url"),
        )

        title_data = TitleData(
            mal_id=external_id,
            name_en=data["title"],
            description_en=tag_remover(data["synopsis"]),
            type=MalParser.convert_type(data["type"]),
            status=MalParser.convert_status(data["status"]),
            popularity=data["popularity"] or 0,
            chapters=data["chapters"] or 0,
            views=data["members"] or 0,
            volumes=data["volumes"] or 0,
            favorites=data["favorites"] or 0,
            rating=data["score"] or 0.0,
            scored_by=data["scored_by"] or 0,
            released_at=(
                datetime.fromisoformat(x) if (x := data["published"]["from"]) else None
            ),
            ended_at=(
                datetime.fromisoformat(x) if (x := data["published"]["to"]) else None
            ),
            genres=[
                genre
                for genre_name in data["genres"]
                if (genre := MalParser.convert_genre(genre_name["name"]))
            ],
            categories=[
                category
                for category_name in data["themes"]
                if (category := MalParser.convert_category(category_name["name"]))
            ],
            authors=[author["name"] for author in data["authors"]],
            alt_names=data["title_synonyms"],
            cover=TitleCover(
                thumbnail=data["images"]["webp"]["small_image_url"],
                original=data["images"]["webp"]["large_image_url"],
            ),
        )

        return SourceTitleData(
            source_metadata=source_metadata,
            title_data=title_data,
        )

    @staticmethod
    def parse_page(data: dict) -> list[SourceTitleData]:
        parsed_titles = []
        for item in data["data"]:
            try:
                parsed_titles.append(MalParser.parse_title(item))
            except (ValueError, KeyError) as e:
                logger.error(
                    f"Skipping Mal title id={item['mal_id']}: {e}", exc_info=True
                )
                continue
            except Exception as e:
                logger.error(
                    f"Unexpected error parsing Mal title id={item['mal_id']}: {e}",
                    exc_info=True,
                )
                continue

        return parsed_titles

    # === Converters ===
    @staticmethod
    def convert_type(data: str) -> TitleType:
        return MalParser._TYPE_MAPPING.get(data.lower(), TitleType.OTHER)

    @staticmethod
    def convert_status(data: str) -> TitleStatus:
        return MalParser._STATUS_MAPPING.get(data.lower(), TitleStatus.UNKNOWN)

    @staticmethod
    def convert_genre(data: str) -> TitleGenre | None:
        return MalParser._GENRE_MAPPING.get(data)

    @staticmethod
    def convert_category(data: str) -> TitleCategory | None:
        return MalParser._CATEGORY_MAPPING.get(data)

    # === Mappings ===
    _GENRE_MAPPING = {
        "Action": TitleGenre.ACTION,
        "Adventure": TitleGenre.ADVENTURE,
        "Avant Garde": TitleGenre.AVANT_GARDE,
        "Award Winning": TitleGenre.AWARD_WINNING,
        "Boys Love": TitleGenre.BOYS_LOVE,
        "Comedy": TitleGenre.COMEDY,
        "Drama": TitleGenre.DRAMA,
        "Fantasy": TitleGenre.FANTASY,
        "Girls Love": TitleGenre.GIRLS_LOVE,
        "Gourmet": TitleGenre.GOURMET,
        "Horror": TitleGenre.HORROR,
        "Mystery": TitleGenre.MYSTERY,
        "Romance": TitleGenre.ROMANCE,
        "Sci-Fi": TitleGenre.SCIENCE_FICTION,
        "Slice of Life": TitleGenre.SLICE_OF_LIFE,
        "Sports": TitleGenre.SPORTS,
        "Supernatural": TitleGenre.SUPERNATURAL,
        "Suspense": TitleGenre.SUSPENSE,
    }

    _CATEGORY_MAPPING = {
        "Adult Cast": TitleCategory.ADULT_CAST,
        "Anthropomorphic": TitleCategory.ANTHROPOMORPHIC,
        "CGDCT": TitleCategory.CGDCT,
        "Childcare": TitleCategory.CHILDCARE,
        "Combat Sports": TitleCategory.COMBAT_SPORTS,
        "Crossdressing": TitleCategory.CROSSDRESSING,
        "Delinquents": TitleCategory.DELINQUENTS,
        "Detective": TitleCategory.DETECTIVE,
        "Educational": TitleCategory.EDUCATIONAL,
        "Gag Humor": TitleCategory.GAG_HUMOR,
        "Gore": TitleCategory.GORE,
        "Harem": TitleCategory.HAREM,
        "High Stakes Game": TitleCategory.HIGH_STAKES_GAME,
        "Historical": TitleCategory.HISTORICAL,
        "Idols (Female)": TitleCategory.IDOLS_FEMALE,
        "Idols (Male)": TitleCategory.IDOLS_MALE,
        "Isekai": TitleCategory.ISEKAI,
        "Iyashikei": TitleCategory.IYASHIKEI,
        "Love Polygon": TitleCategory.LOVE_POLYGON,
        "Love Status Quo": TitleCategory.LOVE_STATUS_QUO,
        "Magical Sex Shift": TitleCategory.MAGICAL_SEX_SHIFT,
        "Mahou Shoujo": TitleCategory.MAHOU_SHOUJO,
        "Martial Arts": TitleCategory.MARTIAL_ARTS,
        "Mecha": TitleCategory.MECHA,
        "Medical": TitleCategory.MEDICAL,
        "Memoir": TitleCategory.MEMOIR,
        "Military": TitleCategory.MILITARY,
        "Music": TitleCategory.MUSIC,
        "Mythology": TitleCategory.MYTHOLOGY,
        "Organized Crime": TitleCategory.MAFIA,
        "Otaku Culture": TitleCategory.OTAKU_CULTURE,
        "Parody": TitleCategory.PARODY,
        "Performing Arts": TitleCategory.PERFORMING_ARTS,
        "Pets": TitleCategory.PETS,
        "Psychological": TitleCategory.PSYCHOLOGICAL,
        "Racing": TitleCategory.RACING,
        "Reincarnation": TitleCategory.REINCARNATION,
        "Reverse Harem": TitleCategory.REVERSE_HAREM,
        "Samurai": TitleCategory.SAMURAI,
        "School": TitleCategory.SCHOOL,
        "Showbiz": TitleCategory.SHOWBIZ,
        "Space": TitleCategory.SPACE,
        "Strategy Game": TitleCategory.STRATEGY_GAME,
        "Super Power": TitleCategory.SUPER_POWER,
        "Survival": TitleCategory.SURVIVAL,
        "Team Sports": TitleCategory.TEAM_SPORTS,
        "Time Travel": TitleCategory.TIME_TRAVEL,
        "Urban Fantasy": TitleCategory.URBAN_FANTASY,
        "Vampire": TitleCategory.VAMPIRE,
        "Video Game": TitleCategory.VIDEO_GAME,
        "Villainess": TitleCategory.VILLAINESS,
        "Visual Arts": TitleCategory.VISUAL_ARTS,
        "Workplace": TitleCategory.WORKPLACE,
    }

    _TYPE_MAPPING = {
        "manga": TitleType.MANGA,
        "manhwa": TitleType.MANHWA,
        "manhua": TitleType.MANHUA,
        "light novel": TitleType.LIGHT_NOVEL,
        "novel": TitleType.NOVEL,
        "one-shot": TitleType.ONESHOT,
        "doujinshi": TitleType.DOUJIN,
        "webtoon": TitleType.WEBTOON,
    }

    _STATUS_MAPPING = {
        "publishing": TitleStatus.ONGOING,
        "finished": TitleStatus.FINISHED,
        "discontinued": TitleStatus.DISCONTINUED,
        "on hiatus": TitleStatus.FROZEN,
        "upcoming": TitleStatus.ANONS,
    }
