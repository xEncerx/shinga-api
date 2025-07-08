from pydantic import BaseModel

from sqlmodel import SQLModel, Field
from typing import Optional
from enum import Enum


class Genre(BaseModel):
    ru: str
    en: str


class TitleCover(SQLModel):
    url: str | None
    small_url: str | None
    large_url: str | None


class TitleType(str, Enum):
    # * Check ../utils/type_converter.py for conversion methods from different providers
    MANGA = "manga"
    NOVEL = "novel"
    LIGHT_NOVEL = "light novel"
    ONESHOT = "one-shot"
    DOUJIN = "doujinshi"
    MANHWA = "manhwa"
    MANHUA = "manhua"
    COMICS = "comics"
    WEBTOON = "webtoon"
    OTHER = "other"


class TitleReleaseTime(SQLModel):
    from_: str | None = Field(description="Release start date in ISO 8601 format")
    to: str | None = Field(description="Release end date in ISO 8601 format, if applicable")


class TitleDescription(SQLModel):
    en: str | None
    ru: str | None


class TitleStatus(str, Enum):
    # * Check ../utils/status_converter.py for conversion methods from different providers
    ONGOING = "ongoing"
    FINISHED = "finished"
    DISCONTINUED = "discontinued"
    LICENSED = "licensed"
    FROZEN = "frozen"
    ANONS = "anons"
    UNKNOWN = "unknown"


class SourceProvider(str, Enum):
    MAL = "mal"
    REMANGA = "remanga"
    SHIKIMORI = "shiki"
    CUSTOM = "custom"


class TitleGenre(Enum):
    @classmethod
    def get(
        cls,
        en: str | None = None,
        ru: str | None = None,
    ) -> Optional["TitleGenre"]:
        """Gets a genre by its English or Russian name."""
        if not en and not ru:
            raise ValueError("At least one of 'en' or 'ru' must be provided.")
        for genre in cls:
            if ru and genre.value.ru.lower() == ru.strip().lower():
                return genre
            if en and genre.value.en.lower() == en.strip().lower():
                return genre

        # TODO: Remove print later
        print(f"Genre '{en}' not found.")
        return None

    ACTION = Genre(ru="Экшен", en="Action")
    ADVENTURE = Genre(ru="Приключения", en="Adventure")
    AVANT_GARDE = Genre(ru="Авангард", en="Avant Garde")
    AWARD_WINNING = Genre(ru="Лауреат наград", en="Award Winning")
    GENDER_INTRIGUE = Genre(ru="Гендерная интрига", en="Gender Intrigue")
    HEROIC_FANTASY = Genre(ru="Героическое фэнтези", en="Heroic Fantasy")
    BOYS_LOVE = Genre(ru="Мужская любовь", en="Boys Love")
    COMEDY = Genre(ru="Комедия", en="Comedy")
    DRAMA = Genre(ru="Драма", en="Drama")
    COMBAT = Genre(ru="Боевик", en="Combat")
    HUMOR = Genre(ru="Юмор", en="Humor")
    MURIM = Genre(ru="Мурим", en="Murim")
    SCHOOL_LIFE = Genre(ru="Школьная жизнь", en="School Life")
    FANTASTIC = Genre(ru="Фантастика", en="Fantastic")
    THRILLER = Genre(ru="Триллер", en="Thriller")
    TRAGEDY = Genre(ru="Трагедия", en="Tragedy")
    PSYCHOLOGY = Genre(ru="Психология", en="Psychology")
    POST_APOCALYPTIC = Genre(ru="Постапокалиптика", en="Post-Apocalyptic")
    ELEMENTS_OF_HUMOR = Genre(ru="Элементы юмора", en="Elements of Humor")
    KODOMO = Genre(ru="Кодомо", en="Kodomo")
    KIDS = Genre(ru="Детский", en="Kids")
    CYBERPUNK = Genre(ru="Киберпанк", en="Cyberpunk")
    HISTORY = Genre(ru="История", en="History")
    FANTASY = Genre(ru="Фэнтези", en="Fantasy")
    GIRLS_LOVE = Genre(ru="Тянки-лав", en="Girls Love")
    GOURMET = Genre(ru="Гурман", en="Gourmet")
    HORROR = Genre(ru="Ужасы", en="Horror")
    MYSTERY = Genre(ru="Мистика", en="Mystery")
    ROMANCE = Genre(ru="Романтика", en="Romance")
    SCI_FI = Genre(ru="Научная фантастика", en="Sci-Fi")
    SLICE_OF_LIFE = Genre(ru="Повседневность", en="Slice of Life")
    SPORTS = Genre(ru="Спорт", en="Sports")
    SUPERNATURAL = Genre(ru="Сверхъестественное", en="Supernatural")
    SUSPENSE = Genre(ru="Саспенс", en="Suspense")
    SEINEN = Genre(ru="Сэйнэн", en="Seinen")
    SHOUNEN = Genre(ru="Сёнэн", en="Shounen")
    DOUJINSHI = Genre(ru="Додзинси", en="Doujinshi")
    SHOUJO = Genre(ru="Сёдзё", en="Shoujo")
    JOSEI = Genre(ru="Дзёсэй", en="Josei")
    YAOI = Genre(ru="Яой", en="Yaoi")
    ECCHI = Genre(ru="Этти", en="Ecchi")
    EROTICA = Genre(ru="Эротика", en="Erotica")
    HENTAI = Genre(ru="Хентай", en="Hentai")
    ADULT_CAST = Genre(ru="Взрослый состав", en="Adult Cast")
    ANTHROPOMORPHIC = Genre(ru="Антропоморфизм", en="Anthropomorphic")
    CGDCT = Genre(ru="Милые девушки делают милые вещи", en="CGDCT")
    CHILDCARE = Genre(ru="Уход за детьми", en="Childcare")
    COMBAT_SPORTS = Genre(ru="Боевые виды спорта", en="Combat Sports")
    CROSSDRESSING = Genre(ru="Кроссдрессинг", en="Crossdressing")
    DELINQUENTS = Genre(ru="Делинквенты", en="Delinquents")
    DETECTIVE = Genre(ru="Детектив", en="Detective")
    EDUCATIONAL = Genre(ru="Образовательный", en="Educational")
    GAG_HUMOR = Genre(ru="Гэг-юмор", en="Gag Humor")
    GORE = Genre(ru="Жестокость", en="Gore")
    HAREM = Genre(ru="Гарем", en="Harem")
    HIGH_STAKES_GAME = Genre(ru="Игры с высокими ставками", en="High Stakes Game")
    HISTORICAL = Genre(ru="Исторический", en="Historical")
    IDOLS_FEMALE = Genre(ru="Айдолы (женщины)", en="Idols (Female)")
    IDOLS_MALE = Genre(ru="Айдолы (мужчины)", en="Idols (Male)")
    ISEKAI = Genre(ru="Исэкай", en="Isekai")
    IYASHIKEI = Genre(ru="Иясикэй", en="Iyashikei")
    LOVE_POLYGON = Genre(ru="Любовный многоугольник", en="Love Polygon")
    LOVE_STATUS_QUO = Genre(ru="Статус-кво в любви", en="Love Status Quo")
    MAGICAL_SEX_SHIFT = Genre(ru="Магическая смена пола", en="Magical Sex Shift")
    MAHOU_SHOUJO = Genre(ru="Махо-сёдзё", en="Mahou Shoujo")
    MARTIAL_ARTS = Genre(ru="Боевые искусства", en="Martial Arts")
    MECHA = Genre(ru="Меха", en="Mecha")
    MEDICAL = Genre(ru="Медицинский", en="Medical")
    MEMOIR = Genre(ru="Мемуары", en="Memoir")
    MILITARY = Genre(ru="Военный", en="Military")
    MUSIC = Genre(ru="Музыка", en="Music")
    MYTHOLOGY = Genre(ru="Мифология", en="Mythology")
    ORGANIZED_CRIME = Genre(ru="Организованная преступность", en="Organized Crime")
    OTAKU_CULTURE = Genre(ru="Отаку-культура", en="Otaku Culture")
    PARODY = Genre(ru="Пародия", en="Parody")
    PERFORMING_ARTS = Genre(ru="Исполнительские искусства", en="Performing Arts")
    PETS = Genre(ru="Питомцы", en="Pets")
    PSYCHOLOGICAL = Genre(ru="Психологическое", en="Psychological")
    RACING = Genre(ru="Гонки", en="Racing")
    REINCARNATION = Genre(ru="Реинкарнация", en="Reincarnation")
    REVERSE_HAREM = Genre(ru="Обратный гарем", en="Reverse Harem")
    SAMURAI = Genre(ru="Самураи", en="Samurai")
    SCHOOL = Genre(ru="Школа", en="School")
    SHOWBIZ = Genre(ru="Шоу-бизнес", en="Showbiz")
    SPACE = Genre(ru="Космос", en="Space")
    STRATEGY_GAME = Genre(ru="Стратегические игры", en="Strategy Game")
    SUPER_POWER = Genre(ru="Суперсила", en="Super Power")
    SURVIVAL = Genre(ru="Выживание", en="Survival")
    TEAM_SPORTS = Genre(ru="Командный спорт", en="Team Sports")
    TIME_TRAVEL = Genre(ru="Путешествия во времени", en="Time Travel")
    URBAN_FANTASY = Genre(ru="Городское фэнтези", en="Urban Fantasy")
    VAMPIRE = Genre(ru="Вампиры", en="Vampire")
    VIDEO_GAME = Genre(ru="Видеоигры", en="Video Game")
    VILLAINESS = Genre(ru="Злодейка", en="Villainess")
    VISUAL_ARTS = Genre(ru="Визуальные искусства", en="Visual Arts")
    WORKPLACE = Genre(ru="Рабочее место", en="Workplace")
