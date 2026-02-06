from src.core import logger
from ..base_parser import *


class ShikimoriParser(BaseParser):
    @staticmethod
    def parse_title(data: dict) -> SourceTitleData:
        external_id = str(data["id"])
        mal_id = int(data["malId"]) if data.get("malId") else None

        source_metadata = SourceMetadata(
            source=Source.SHIKIMORI,
            external_id=external_id,
            source_url=data.get("url"),
        )

        title_data = TitleData(
            mal_id=mal_id,
            name_ru=data["russian"] or data["licenseNameRu"],
            name_en=data["english"] or data["name"],
            description_ru=tag_remover(data["description"]),
            type=ShikimoriParser.convert_type(data["kind"]),
            status=ShikimoriParser.convert_status(data["status"]),
            chapters=data["chapters"] or 0,
            volumes=data["volumes"] or 0,
            rating=data["score"] or 0.0,
            favorites=sum(i["count"] for i in data["statusesStats"]),
            scored_by=sum(i["count"] for i in data["scoresStats"]),
            released_at=(
                datetime.strptime(x, "%Y-%m-%d")
                if (x := data["airedOn"]["date"])
                else None
            ),
            ended_at=(
                datetime.strptime(x, "%Y-%m-%d")
                if (x := data["releasedOn"]["date"])
                else None
            ),
            genres=[
                genre
                for genre_name in data["genres"]
                if genre_name["kind"] == "genre"
                and (genre := ShikimoriParser.convert_genre(genre_name["name"]))
            ],
            categories=[
                category
                for category_name in data["genres"]
                if category_name["kind"] == "theme"
                and (
                    category := ShikimoriParser.convert_category(category_name["name"])
                )
            ],
            authors=[i["person"].get("name", "unknown") for i in data["personRoles"]],
            alt_names=data["synonyms"],
            cover=TitleCover(
                original=data["poster"]["originalUrl"] if data["poster"] else None
            ),
        )

        return SourceTitleData(
            source_metadata=source_metadata,
            title_data=title_data,
        )

    @staticmethod
    def parse_page(data: dict) -> list[SourceTitleData]:
        parsed_titles = []
        for item in data["data"]["mangas"]:
            try:
                parsed_titles.append(ShikimoriParser.parse_title(item))
            except (ValueError, KeyError) as e:
                logger.error(
                    f"Skipping Shikimori title id={item['id']}: {e}",
                    exc_info=True,
                )
                continue
            except Exception as e:
                logger.error(
                    f"Unexpected error parsing Shikimori title id={item['id']}: {e}",
                    exc_info=True,
                )
                continue

        return parsed_titles

    # === Converters ===
    @staticmethod
    def convert_type(data: str) -> TitleType:
        return ShikimoriParser._TYPE_MAPPING.get(data.lower(), TitleType.OTHER)

    @staticmethod
    def convert_status(data: str) -> TitleStatus:
        return ShikimoriParser._STATUS_MAPPING.get(data.lower(), TitleStatus.UNKNOWN)

    @staticmethod
    def convert_genre(data: str) -> TitleGenre | None:
        return ShikimoriParser._GENRE_MAPPING.get(data)

    @staticmethod
    def convert_category(data: str) -> TitleCategory | None:
        return ShikimoriParser._CATEGORY_MAPPING.get(data)

    # === Mappings ===
    _GENRE_MAPPING = {
        "Action": TitleGenre.ACTION,
        "Adventure": TitleGenre.ADVENTURE,
        "Avant Garde": TitleGenre.AVANT_GARDE,
        "Boys Love": TitleGenre.BOYS_LOVE,
        "Comedy": TitleGenre.COMEDY,
        "Drama": TitleGenre.DRAMA,
        "Ecchi": TitleGenre.ECCHI,
        "Erotica": TitleGenre.EROTICA,
        "Fantasy": TitleGenre.FANTASY,
        "Girls Love": TitleGenre.GIRLS_LOVE,
        "Gourmet": TitleGenre.GOURMET,
        "Hentai": TitleGenre.HENTAI,
        "Horror": TitleGenre.HORROR,
        "Mystery": TitleGenre.MYSTERY,
        "Romance": TitleGenre.ROMANCE,
        "Sci-Fi": TitleGenre.SCIENCE_FICTION,
        "Slice of Life": TitleGenre.SLICE_OF_LIFE,
        "Sports": TitleGenre.SPORTS,
        "Supernatural": TitleGenre.SUPERNATURAL,
        "Suspense": TitleGenre.SUSPENSE,
        "Yaoi": TitleGenre.BOYS_LOVE,
        "Yuri": TitleGenre.GIRLS_LOVE,
    }

    _CATEGORY_MAPPING = {
        "Adult Cast": TitleCategory.ADULT_CAST,
        "Anthropomorphic": TitleCategory.ANTHROPOMORPHIC,
        "Award Winning": TitleCategory.AWARD_WINNING,
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
        "light_novel": TitleType.LIGHT_NOVEL,
        "novel": TitleType.NOVEL,
        "one_shot": TitleType.ONESHOT,
        "doujin": TitleType.DOUJIN,
    }

    _STATUS_MAPPING = {
        "ongoing": TitleStatus.ONGOING,
        "released": TitleStatus.FINISHED,
        "discontinued": TitleStatus.DISCONTINUED,
        "paused": TitleStatus.FROZEN,
        "anons": TitleStatus.ANONS,
    }
