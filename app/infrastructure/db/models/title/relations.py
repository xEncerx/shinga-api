from sqlmodel import SQLModel
from enum import Enum

class TitleGenre(SQLModel):
    ru: str | None
    en: str | None


class TitleCover(SQLModel):
    url: str | None
    small_url: str | None
    large_url: str | None



class TitleType(str, Enum):
    MANGA = "manga"
    NOVEL = "novel"
    LIGHT_NOVEL = "light novel"
    ONESHOT = "one-shot"
    DOUJIN = "doujinshi"
    MANHWA = "manhwa"
    MANHUA = "manhua"
    WEBTOON = "webtoon"
    OTHER = "other"

class TitleReleaseTime(SQLModel):
    from_: str | None
    to: str | None

class TitleDescription(SQLModel):
    en: str | None
    ru: str | None

class TitleStatus(str, Enum):
    ONGOING = "publishing"
    FINISHED = "finished"
    DISCONTINUED = "discontinued"
    FROZEN = "on hiatus"
    ANONS = "upcoming"
    UNKNOWN = "unknown"

class SourceProvider(str, Enum):
    MAL = "mal"
    REMANGA = "remanga"
    SHIKIMORI = "shikimori"
    CUSTOM = "custom"

class Genre:
    @classmethod
    def get(cls, en: str) -> TitleGenre | None:
        """Returns the TitleGenre object for the given English name."""
        for _, genre in cls.__dict__.items():
            if isinstance(genre, TitleGenre) and genre.en == en:
                return genre
            
        print(f"Genre '{en}' not found.")
        return None

    ACTION = TitleGenre(ru="Экшен", en="Action")
    ADVENTURE = TitleGenre(ru="Приключения", en="Adventure")
    AVANT_GARDE = TitleGenre(ru="Авангард", en="Avant Garde")
    AWARD_WINNING = TitleGenre(ru="Лауреат наград", en="Award Winning")
    BOYS_LOVE = TitleGenre(ru="Мужская любовь", en="Boys Love")
    COMEDY = TitleGenre(ru="Комедия", en="Comedy")
    DRAMA = TitleGenre(ru="Драма", en="Drama")
    FANTASY = TitleGenre(ru="Фэнтези", en="Fantasy")
    GIRLS_LOVE = TitleGenre(ru="Тянки-лав", en="Girls Love")
    GOURMET = TitleGenre(ru="Гурман", en="Gourmet")
    HORROR = TitleGenre(ru="Хоррор", en="Horror")
    MYSTERY = TitleGenre(ru="Мистика", en="Mystery")
    ROMANCE = TitleGenre(ru="Романтика", en="Romance")
    SCI_FI = TitleGenre(ru="Научная фантастика", en="Sci-Fi")
    SLICE_OF_LIFE = TitleGenre(ru="Повседневность", en="Slice of Life")
    SPORTS = TitleGenre(ru="Спорт", en="Sports")
    SUPERNATURAL = TitleGenre(ru="Сверхъестественное", en="Supernatural")
    SUSPENSE = TitleGenre(ru="Саспенс", en="Suspense")
    ECCHI = TitleGenre(ru="Этти", en="Ecchi")
    EROTICA = TitleGenre(ru="Эротика", en="Erotica")
    HENTAI = TitleGenre(ru="Хентай", en="Hentai")
    ADULT_CAST = TitleGenre(ru="Взрослый состав", en="Adult Cast")
    ANTHROPOMORPHIC = TitleGenre(ru="Антропоморфизм", en="Anthropomorphic")
    CGDCT = TitleGenre(ru="Милые девушки делают милые вещи", en="CGDCT")
    CHILDCARE = TitleGenre(ru="Уход за детьми", en="Childcare")
    COMBAT_SPORTS = TitleGenre(ru="Боевые виды спорта", en="Combat Sports")
    CROSSDRESSING = TitleGenre(ru="Кроссдрессинг", en="Crossdressing")
    DELINQUENTS = TitleGenre(ru="Делинквенты", en="Delinquents")
    DETECTIVE = TitleGenre(ru="Детектив", en="Detective")
    EDUCATIONAL = TitleGenre(ru="Образовательный", en="Educational")
    GAG_HUMOR = TitleGenre(ru="Гэг-юмор", en="Gag Humor")
    GORE = TitleGenre(ru="Жестокость", en="Gore")
    HAREM = TitleGenre(ru="Гарем", en="Harem")
    HIGH_STAKES_GAME = TitleGenre(ru="Игры с высокими ставками", en="High Stakes Game")
    HISTORICAL = TitleGenre(ru="Исторический", en="Historical")
    IDOLS_FEMALE = TitleGenre(ru="Айдолы (женщины)", en="Idols (Female)")
    IDOLS_MALE = TitleGenre(ru="Айдолы (мужчины)", en="Idols (Male)")
    ISEKAI = TitleGenre(ru="Исэкай", en="Isekai")
    IYASHIKEI = TitleGenre(ru="Иясикэй", en="Iyashikei")
    LOVE_POLYGON = TitleGenre(ru="Любовный многоугольник", en="Love Polygon")
    LOVE_STATUS_QUO = TitleGenre(ru="Статус-кво в любви", en="Love Status Quo")
    MAGICAL_SEX_SHIFT = TitleGenre(ru="Магическая смена пола", en="Magical Sex Shift")
    MAHOU_SHOUJO = TitleGenre(ru="Махо-сёдзё", en="Mahou Shoujo")
    MARTIAL_ARTS = TitleGenre(ru="Боевые искусства", en="Martial Arts")
    MECHA = TitleGenre(ru="Меха", en="Mecha")
    MEDICAL = TitleGenre(ru="Медицинский", en="Medical")
    MEMOIR = TitleGenre(ru="Мемуары", en="Memoir")
    MILITARY = TitleGenre(ru="Военный", en="Military")
    MUSIC = TitleGenre(ru="Музыка", en="Music")
    MYTHOLOGY = TitleGenre(ru="Мифология", en="Mythology")
    ORGANIZED_CRIME = TitleGenre(ru="Организованная преступность", en="Organized Crime")
    OTAKU_CULTURE = TitleGenre(ru="Отаку-культура", en="Otaku Culture")
    PARODY = TitleGenre(ru="Пародия", en="Parody")
    PERFORMING_ARTS = TitleGenre(ru="Исполнительские искусства", en="Performing Arts")
    PETS = TitleGenre(ru="Питомцы", en="Pets")
    PSYCHOLOGICAL = TitleGenre(ru="Психологическое", en="Psychological")
    RACING = TitleGenre(ru="Гонки", en="Racing")
    REINCARNATION = TitleGenre(ru="Реинкарнация", en="Reincarnation")
    REVERSE_HAREM = TitleGenre(ru="Обратный гарем", en="Reverse Harem")
    SAMURAI = TitleGenre(ru="Самураи", en="Samurai")
    SCHOOL = TitleGenre(ru="Школа", en="School")
    SHOWBIZ = TitleGenre(ru="Шоу-бизнес", en="Showbiz")
    SPACE = TitleGenre(ru="Космос", en="Space")
    STRATEGY_GAME = TitleGenre(ru="Стратегические игры", en="Strategy Game")
    SUPER_POWER = TitleGenre(ru="Суперсила", en="Super Power")
    SURVIVAL = TitleGenre(ru="Выживание", en="Survival")
    TEAM_SPORTS = TitleGenre(ru="Командный спорт", en="Team Sports")
    TIME_TRAVEL = TitleGenre(ru="Путешествия во времени", en="Time Travel")
    URBAN_FANTASY = TitleGenre(ru="Городское фэнтези", en="Urban Fantasy")
    VAMPIRE = TitleGenre(ru="Вампиры", en="Vampire")
    VIDEO_GAME = TitleGenre(ru="Видеоигры", en="Video Game")
    VILLAINESS = TitleGenre(ru="Злодейка", en="Villainess")
    VISUAL_ARTS = TitleGenre(ru="Визуальные искусства", en="Visual Arts")
    WORKPLACE = TitleGenre(ru="Рабочее место", en="Workplace")