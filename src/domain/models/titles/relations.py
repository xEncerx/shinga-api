from dataclasses import dataclass
from pydantic import BaseModel
from enum import Enum

from src.core.settings import settings

__all__ = [
    "TitleType",
    "TitleStatus",
    "TitleGenre",
    "TitleCategory",
    "TitleCover",
]


class TitleCover(BaseModel):
    thumbnail: str | None = None
    original: str | None = None

    @staticmethod
    def pending() -> "TitleCover":
        return TitleCover(
            thumbnail=settings.PENDING_COVER_URL,
            original=settings.PENDING_COVER_URL,
        )


class TitleType(str, Enum):
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


class TitleStatus(str, Enum):
    ONGOING = "ongoing"
    FINISHED = "finished"
    DISCONTINUED = "discontinued"
    LICENSED = "licensed"
    FROZEN = "frozen"
    ANONS = "anons"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class TitleGenreDetail:
    ru: str
    en: str


class TitleGenre(TitleGenreDetail, Enum):
    ACTION = "Экшен", "Action"
    ADVENTURE = "Приключения", "Adventure"
    AVANT_GARDE = "Авангард", "Avant garde"
    AWARD_WINNING = "Лауреат премий", "Award winning"
    BOYS_LOVE = "Яой", "Boy's love"
    COMEDY = "Комедия", "Comedy"
    CYBERPUNK = "Киберпанк", "Cyberpunk"
    DEMOGRAPHY_JOSEI = "Дзёсэй", "Josei"
    DEMOGRAPHY_KODOMO = "Кодомо", "Kodomo"
    DEMOGRAPHY_SEINEN = "Сэйнэн", "Seinen"
    DEMOGRAPHY_SHOUJO = "Сёдзё", "Shoujo"
    DEMOGRAPHY_SHOUNEN = "Сёнэн", "Shounen"
    DETECTIVE = "Детектив", "Detective"
    DOUJINSHI = "Додзинси", "Doujinshi"
    DRAMA = "Драма", "Drama"
    ECCHI = "Этти", "Ecchi"
    EROTICA = "Эротика", "Erotica"
    FANTASY = "Фэнтези", "Fantasy"
    GAG_HUMOR = "Элементы юмора", "Gag humor"
    GENDER_BENDER = "Гендерная интрига", "Gender bender"
    GIRLS_LOVE = "Юри", "Girl's love"
    GOURMET = "Гурме", "Gourmet"
    HAREM = "Гарем", "Harem"
    HENTAI = "Хентай", "Hentai"
    HEROIC_FANTASY = "Героическое фэнтези", "Heroic fantasy"
    HISTORICAL = "История", "Historical"
    HORROR = "Ужасы", "Horror"
    ISEKAI = "Исекай", "Isekai"
    MAHOU_SHOUJO = "Махо-сёдзё", "Mahou shoujo"
    MARTIAL_ARTS = "Боевые искусства", "Martial arts"
    MECHA = "Меха", "Mecha"
    MURIM = "Мурим", "Murim"
    MYSTERY = "Мистика", "Mystery"
    POST_APOCALYPTIC = "Постапокалиптика", "Post-apocalyptic"
    PSYCHOLOGICAL = "Психология", "Psychological"
    ROMANCE = "Романтика", "Romance"
    SCHOOL_LIFE = "Школьники", "School life"
    SCIENCE_FICTION = "Научная фантастика", "Science fiction"
    SLICE_OF_LIFE = "Повседневность", "Slice of life"
    SPORTS = "Спорт", "Sports"
    STUDENT_LIFE = "Студенты", "Student life"
    SUPERNATURAL = "Сверхъестественное", "Supernatural"
    SUSPENSE = "Триллер", "Suspense"
    TRAGEDY = "Трагедия", "Tragedy"
    UNKNOWN = "Неизвестно", "Unknown"


@dataclass(frozen=True)
class TitleCategoryDetail:
    ru: str
    en: str


class TitleCategory(TitleCategoryDetail, Enum):
    ADULT_CAST = "Взрослые персонажи", "Adult cast"
    ALCHEMY = "Алхимия", "Alchemy"
    AMNESIA = "Амнезия", "Amnesia"
    ANGELS = "Ангелы", "Angels"
    ANIME = "Аниме", "Anime"
    ANTIHERO = "Антигерой", "Antihero"
    ANTHOLOGY = "Антология", "Anthology"
    ANTHROPOMORPHIC = "Антропоморфизм", "Anthropomorphic"
    APOCALYPSE = "Апокалипсис", "Apocalypse"
    ARISTOCRACY = "Аристократия", "Aristocracy"
    ARMY = "Армия", "Army"
    ARTIFACTS = "Артефакты", "Artifacts"
    AWARD_WINNING = "Лауреат премий", "Award winning"
    BEASTMEN = "Зверолюди", "Beastmen"
    BLACKMAIL = "Шантаж", "Blackmail"
    CGDCT = "Милые девушки", "CGDCT"
    CHILDCARE = "Уход за детьми", "Childcare"
    COLORED = "В цвете", "Colored"
    COMBAT_SPORTS = "Боевые виды спорта", "Combat sports"
    COOKING = "Кулинария", "Cooking"
    CRIME = "Криминал", "Crime"
    CROSSDRESSING = "Переодевание", "Crossdressing"
    CRUEL_WORLD = "Жестокий мир", "Cruel world"
    CULTIVATION = "Культивация", "Cultivation"
    DELINQUENTS = "Хулиганы", "Delinquents"
    DEMON_LORD = "Владыка демонов", "Demon lord"
    DEMONS = "Демоны", "Demons"
    DETECTIVE = "Детектив", "Detective"
    DUNGEONS = "Подземелья", "Dungeons"
    DYSTOPIA = "Антиутопия", "Dystopia"
    EDUCATIONAL = "Образовательное", "Educational"
    EDUTAINMENT = "Обучающее развлечение", "Edutainment"
    FEMALE_PROTAGONIST = "ГГ женщина", "Female protagonist"
    FRIENDSHIP = "Дружба", "Friendship"
    FUTURE = "Будущее", "Future"
    GAG_HUMOR = "Гэг-юмор", "Gag humor"
    GAME_ELEMENTS = "Игровые элементы", "Game elements"
    GAMERS = "Геймеры", "Gamers"
    GODS = "Боги", "Gods"
    GORE = "Жестокость", "Gore"
    GUILDS = "Гильдии", "Guilds"
    GYARU = "Гяру", "Gyaru"
    HAREM = "Гарем", "Harem"
    HIDDEN_IDENTITY = "Скрытая личность", "Hidden identity"
    HIGH_STAKES_GAME = "Игра на выживание", "High stakes game"
    HIKIKOMORI = "Хикикомори", "Hikikomori"
    HISTORICAL = "Исторический", "Historical"
    IDOLS_FEMALE = "Идолы (женские)", "Idols (Female)"
    IDOLS_MALE = "Идолы (мужские)", "Idols (Male)"
    INTELLIGENT_RACES = "Разумные расы", "Intelligent races"
    ISEKAI = "Исекай", "Isekai"
    ISEKAI_MEMORIES = "Воспоминания из другого мира", "Isekai memories"
    IYASHIKEI = "Исцеляющее", "Iyashikei"
    JOSEI = "Дзёсэй", "Josei"
    KNIGHTS = "Рыцари", "Knights"
    LOLI = "Лоли", "Loli"
    LOVE_POLYGON = "Любовный многоугольник", "Love polygon"
    LOVE_STATUS_QUO = "Статус-кво отношений", "Love status quo"
    MAFIA = "Организованная преступность", "Organized crime"
    MAGIC = "Магия", "Magic"
    MAGIC_ACADEMY = "Магическая академия", "Magic academy"
    MAGICAL_CREATURES = "Волшебные существа", "Magical creatures"
    MAGICAL_SEX_SHIFT = "Магическая смена пола", "Magical sex shift"
    MAHOU_SHOUJO = "Махо-сёдзё", "Mahou shoujo"
    MAIDS = "Горничные", "Maids"
    MALE_PROTAGONIST = "ГГ мужчина", "Male protagonist"
    MARTIAL_ARTS = "Боевые искусства", "Martial arts"
    MECHA = "Меха", "Mecha"
    MEDICAL = "Медицина", "Medical"
    MEDIEVAL = "Средневековье", "Medieval"
    MEMOIR = "Мемуары", "Memoir"
    MERCENARIES = "Наёмники", "Mercenaries"
    MILITARY = "Военное", "Military"
    MONSTERS = "Монстры", "Monsters"
    MUSIC = "Музыка", "Music"
    MYTHOLOGY = "Мифология", "Mythology"
    NINJA = "Ниндзя", "Ninja"
    NON_HUMAN_PROTAGONIST = "ГГ не человек", "Non-human protagonist"
    OFFICE_WORKERS = "Офисные работники", "Office workers"
    OTAKU_CULTURE = "Отаку-культура", "Otaku culture"
    OVERPOWERED_PROTAGONIST = "ГГ имба", "Overpowered protagonist"
    PARODY = "Пародия", "Parody"
    PERFORMING_ARTS = "Исполнительское искусство", "Performing arts"
    PET_COMPANIONS = "Животные компаньоны", "Pet companions"
    PETS = "Питомцы", "Pets"
    POLICE = "Полиция", "Police"
    POLITICS = "Политика", "Politics"
    POWER_STRUGGLE = "Борьба за власть", "Power struggle"
    PSYCHOLOGICAL = "Психологическое", "Psychological"
    RACING = "Гонки", "Racing"
    RANKS_OF_POWER = "Ранги силы", "Ranks of power"
    REINCARNATION = "Реинкарнация", "Reincarnation"
    REVENGE = "Месть", "Revenge"
    REVERSE_HAREM = "Обратный гарем", "Reverse harem"
    ROBOTS = "Роботы", "Robots"
    SAMURAI = "Самураи", "Samurai"
    SAVING_THE_WORLD = "Спасение мира", "Saving the world"
    SCHOOL = "Учебное заведение", "School"
    SEINEN = "Сэйнэн", "Seinen"
    SHOUNEN = "Сёнэн", "Shounen"
    SHOWBIZ = "Шоу-бизнес", "Showbiz"
    SINGLE = "Сингл", "Single"
    SKILLS = "Навыки", "Skills"
    SMART_PROTAGONIST = "Умный ГГ", "Smart protagonist"
    SPACE = "Космос", "Space"
    STEAMPUNK = "Стимпанк", "Steampunk"
    STRATEGY_GAME = "Стратегические игры", "Strategy game"
    STUPIDITY = "Упоротость", "Stupidity"
    STUPID_PROTAGONIST = "Тупой ГГ", "Stupid protagonist"
    SUPER_POWER = "Супер силы", "Super power"
    SUPERHEROES = "Супер герои", "Superheroes"
    SURVIVAL = "Выживание", "Survival"
    SWORD_FIGHTING = "Бои на мечах", "Sword fighting"
    SYSTEM = "Система", "System"
    TEACHER_STUDENT = "Учитель / ученик", "Teacher student"
    TEAM_SPORTS = "Командные виды спорта", "Team sports"
    TERRITORY_MANAGEMENT = "Управление территорией", "Territory management"
    TIME_TRAVEL = "Путешествия во времени", "Time travel"
    TRADITIONAL_GAMES = "Традиционные игры", "Traditional games"
    TRUCK_KUN = "Грузовик-сан", "Truck-kun"
    UNDEAD = "Нежить", "Undead"
    URBAN_FANTASY = "Городское фэнтези", "Urban fantasy"
    VAMPIRE = "Вампиры", "Vampire"
    VIDEO_GAME = "Видеоигры", "Video game"
    VILLAINESS = "Злодейка", "Villainess"
    VIOLENCE = "Насилие / жестокость", "Violence"
    VISUAL_ARTS = "Изобразительное искусство", "Visual arts"
    WEB = "Веб", "Web"
    WESTERN = "Вестерн", "Western"
    WORKPLACE = "Рабочее место", "Workplace"
    YONKOMA = "Ёнкома", "Yonkoma"
    ZOMBIES = "Зомби", "Zombies"
    UNKNOWN = "Неизвестно", "Unknown"
