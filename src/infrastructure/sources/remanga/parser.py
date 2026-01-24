from src.core import logger
from ..base_parser import *


class RemangaParser(BaseParser):
    @staticmethod
    def parse_title(data: dict) -> SourceTitleData:
        external_id = data["dir"]
        cover = data.get("cover", {})
        original_cover = cover.get("high") or cover.get("mid")

        source_metadata = SourceMetadata(
            source=Source.REMANGA,
            external_id=external_id,
            source_url=f"https://remanga.org/manga/{external_id}/main",
            extended_data={
                "remanga_id": data["id"],
            },
        )

        title_data = TitleData(
            mal_id=None,
            name_ru=data["main_name"],
            name_en=data["secondary_name"],
            description_ru=(
                tag_remover(desc) if (desc := data.get("description")) else None
            ),
            type=RemangaParser.convert_type(data["type"]["name"]),
            status=RemangaParser.convert_status(data["status"]["name"]),
            chapters=data.get("count_chapters") or 0,
            views=data["total_views"],
            rating=float(data["avg_rating"] or 0),
            favorites=data.get("count_bookmarks") or 0,
            scored_by=data.get("count_rating") or data.get("total_votes") or 0,
            released_at=(
                datetime.strptime(str(year), "%Y")
                if (year := data["issue_year"])
                else None
            ),
            genres=[
                RemangaParser.convert_genre(genre["name"]) for genre in data["genres"]
            ],
            categories=[
                RemangaParser.convert_category(category["name"])
                for category in data["categories"]
            ],
            alt_names=(
                [name for i in data["another_name"].split("/") if (name := i.strip())]
                if data.get("another_name")
                else []
            ),
            cover=TitleCover(
                thumbnail=(
                    "https://remanga.org" + mc
                    if (mc := data["cover"].get("low"))
                    else None
                ),
                original=(
                    "https://remanga.org" + original_cover if original_cover else None
                ),
            ),
        )

        return SourceTitleData(
            source_metadata=source_metadata,
            title_data=title_data,
        )

    @staticmethod
    def parse_page(data: dict) -> list[SourceTitleData]:
        parsed_titles = []
        for item in data["results"]:
            try:
                parsed_titles.append(RemangaParser.parse_title(item))
            except (ValueError, KeyError) as e:
                logger.error(
                    f"Skipping Remanga title id={item['dir']}: {e}",
                    exc_info=True,
                )
                continue
            except Exception as e:
                logger.error(
                    f"Unexpected error parsing Remanga title id={item['dir']}: {e}",
                    exc_info=True,
                )
                continue

        return parsed_titles

    # === Converters ===
    @staticmethod
    def convert_type(data: str) -> TitleType:
        return RemangaParser._TYPE_MAPPING.get(data.lower(), TitleType.OTHER)

    @staticmethod
    def convert_status(data: str) -> TitleStatus:
        return RemangaParser._STATUS_MAPPING.get(data.lower(), TitleStatus.UNKNOWN)

    @staticmethod
    def convert_genre(data: str) -> TitleGenre:
        return RemangaParser._GENRE_MAPPING.get(data, TitleGenre.UNKNOWN)

    @staticmethod
    def convert_category(data: str) -> TitleCategory:
        return RemangaParser._CATEGORY_MAPPING.get(data, TitleCategory.UNKNOWN)

    # === Mappings ===
    _GENRE_MAPPING = {
        "Боевые искусства": TitleGenre.MARTIAL_ARTS,
        "Гарем": TitleGenre.HAREM,
        "Гендерная интрига": TitleGenre.GENDER_BENDER,
        "Героическое фэнтези": TitleGenre.HEROIC_FANTASY,
        "Детектив": TitleGenre.DETECTIVE,
        "Дзёсэй": TitleGenre.DEMOGRAPHY_JOSEI,
        "Додзинси": TitleGenre.DOUJINSHI,
        "Драма": TitleGenre.DRAMA,
        "История": TitleGenre.HISTORICAL,
        "Киберпанк": TitleGenre.CYBERPUNK,
        "Кодомо": TitleGenre.DEMOGRAPHY_KODOMO,
        "Комедия": TitleGenre.COMEDY,
        "Махо-сёдзё": TitleGenre.MAHOU_SHOUJO,
        "Меха": TitleGenre.MECHA,
        "Мистика": TitleGenre.MYSTERY,
        "Мурим": TitleGenre.MURIM,
        "Научная фантастика": TitleGenre.SCIENCE_FICTION,
        "Повседневность": TitleGenre.SLICE_OF_LIFE,
        "Постапокалиптика": TitleGenre.POST_APOCALYPTIC,
        "Приключения": TitleGenre.ADVENTURE,
        "Психология": TitleGenre.PSYCHOLOGICAL,
        "Романтика": TitleGenre.ROMANCE,
        "Сверхъестественное": TitleGenre.SUPERNATURAL,
        "Сёдзё": TitleGenre.DEMOGRAPHY_SHOUJO,
        "Сёдзё-ай": TitleGenre.GIRLS_LOVE,
        "Сёнэн": TitleGenre.DEMOGRAPHY_SHOUNEN,
        "Спорт": TitleGenre.SPORTS,
        "Студенты": TitleGenre.STUDENT_LIFE,
        "Сэйнэн": TitleGenre.DEMOGRAPHY_SEINEN,
        "Трагедия": TitleGenre.TRAGEDY,
        "Триллер": TitleGenre.SUSPENSE,
        "Ужасы": TitleGenre.HORROR,
        "Фантастика": TitleGenre.FANTASY,
        "Фэнтези": TitleGenre.FANTASY,
        "Школьники": TitleGenre.SCHOOL_LIFE,
        "Экшен": TitleGenre.ACTION,
        "Элементы юмора": TitleGenre.GAG_HUMOR,
        "Эротика": TitleGenre.EROTICA,
        "Этти": TitleGenre.ECCHI,
        "Юри": TitleGenre.GIRLS_LOVE,
    }

    _CATEGORY_MAPPING = {
        "Алхимия": TitleCategory.ALCHEMY,
        "Амнезия": TitleCategory.AMNESIA,
        "Ангелы": TitleCategory.ANGELS,
        "Аниме": TitleCategory.ANIME,
        "Антигерой": TitleCategory.ANTIHERO,
        "Антиутопия": TitleCategory.DYSTOPIA,
        "Апокалипсис": TitleCategory.APOCALYPSE,
        "Аристократия": TitleCategory.ARISTOCRACY,
        "Армия": TitleCategory.ARMY,
        "Артефакты": TitleCategory.ARTIFACTS,
        "Боги": TitleCategory.GODS,
        "Бои на мечах": TitleCategory.SWORD_FIGHTING,
        "Борьба за власть": TitleCategory.POWER_STRUGGLE,
        "Будущее": TitleCategory.FUTURE,
        "В цвете": TitleCategory.COLORED,
        "Веб": TitleCategory.WEB,
        "Вестерн": TitleCategory.WESTERN,
        "Видеоигры": TitleCategory.VIDEO_GAME,
        "Владыка демонов": TitleCategory.DEMON_LORD,
        "Волшебные существа": TitleCategory.MAGICAL_CREATURES,
        "Воспоминания из другого мира": TitleCategory.ISEKAI_MEMORIES,
        "Выживание": TitleCategory.SURVIVAL,
        "ГГ женщина": TitleCategory.FEMALE_PROTAGONIST,
        "ГГ имба": TitleCategory.OVERPOWERED_PROTAGONIST,
        "ГГ мужчина": TitleCategory.MALE_PROTAGONIST,
        "ГГ не человек": TitleCategory.NON_HUMAN_PROTAGONIST,
        "Геймеры": TitleCategory.GAMERS,
        "Гильдии": TitleCategory.GUILDS,
        "Горничные": TitleCategory.MAIDS,
        "Грузовик-сан": TitleCategory.TRUCK_KUN,
        "Гяру": TitleCategory.GYARU,
        "Демоны": TitleCategory.DEMONS,
        "Дружба": TitleCategory.FRIENDSHIP,
        "Ёнкома": TitleCategory.YONKOMA,
        "Жестокий мир": TitleCategory.CRUEL_WORLD,
        "Животные компаньоны": TitleCategory.PET_COMPANIONS,
        "Зверолюди": TitleCategory.BEASTMEN,
        "Зомби": TitleCategory.ZOMBIES,
        "Игровые элементы": TitleCategory.GAME_ELEMENTS,
        "Исекай": TitleCategory.ISEKAI,
        "Космос": TitleCategory.SPACE,
        "Криминал": TitleCategory.CRIME,
        "Кулинария": TitleCategory.COOKING,
        "Культивация": TitleCategory.CULTIVATION,
        "Лоли": TitleCategory.LOLI,
        "Магическая академия": TitleCategory.MAGIC_ACADEMY,
        "Магия": TitleCategory.MAGIC,
        "Медицина": TitleCategory.MEDICAL,
        "Месть": TitleCategory.REVENGE,
        "Монстры": TitleCategory.MONSTERS,
        "Музыка": TitleCategory.MUSIC,
        "Навыки": TitleCategory.SKILLS,
        "Наёмники": TitleCategory.MERCENARIES,
        "Насилие / жестокость": TitleCategory.VIOLENCE,
        "Научпоп": TitleCategory.EDUTAINMENT,
        "Нежить": TitleCategory.UNDEAD,
        "Ниндзя": TitleCategory.NINJA,
        "Обратный Гарем": TitleCategory.REVERSE_HAREM,
        "Офисные работники": TitleCategory.OFFICE_WORKERS,
        "Пародия": TitleCategory.PARODY,
        "Подземелья": TitleCategory.DUNGEONS,
        "Политика": TitleCategory.POLITICS,
        "Полиция": TitleCategory.POLICE,
        "Путешествия во времени": TitleCategory.TIME_TRAVEL,
        "Разумные расы": TitleCategory.INTELLIGENT_RACES,
        "Ранги силы": TitleCategory.RANKS_OF_POWER,
        "Реинкарнация": TitleCategory.REINCARNATION,
        "Роботы": TitleCategory.ROBOTS,
        "Рыцари": TitleCategory.KNIGHTS,
        "Самураи": TitleCategory.SAMURAI,
        "Сборник": TitleCategory.ANTHOLOGY,
        "Сингл": TitleCategory.SINGLE,
        "Система": TitleCategory.SYSTEM,
        "Скрытие личности": TitleCategory.HIDDEN_IDENTITY,
        "Спасение мира": TitleCategory.SAVING_THE_WORLD,
        "Средневековье": TitleCategory.MEDIEVAL,
        "Стимпанк": TitleCategory.STEAMPUNK,
        "Супер герои": TitleCategory.SUPERHEROES,
        "Традиционные игры": TitleCategory.TRADITIONAL_GAMES,
        "Тупой ГГ": TitleCategory.STUPID_PROTAGONIST,
        "Умный ГГ": TitleCategory.SMART_PROTAGONIST,
        "Упоротость": TitleCategory.STUPIDITY,
        "Управление территорией": TitleCategory.TERRITORY_MANAGEMENT,
        "Учебное заведение": TitleCategory.SCHOOL,
        "Учитель / ученик": TitleCategory.TEACHER_STUDENT,
        "Хикикомори": TitleCategory.HIKIKOMORI,
        "Шантаж": TitleCategory.BLACKMAIL,
    }

    _TYPE_MAPPING = {
        "манга": TitleType.MANGA,
        "манхва": TitleType.MANHWA,
        "маньхуа": TitleType.MANHUA,
        "западный комикс": TitleType.COMICS,
        "рукомикс": TitleType.COMICS,
        "индонезийский комикс": TitleType.COMICS,
    }

    _STATUS_MAPPING = {
        "продолжается": TitleStatus.ONGOING,
        "закончен": TitleStatus.FINISHED,
        "заморожен": TitleStatus.FROZEN,
        "анонс": TitleStatus.ANONS,
        "лицензировано": TitleStatus.LICENSED,
    }
