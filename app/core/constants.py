from enum import Enum


class MC:
    """Manga Constants"""

    class Section(str, Enum):
        READING = "читаю"
        PLANNED = "на будущие"
        COMPLETED = "прочитано"
        NOT_READ = "не читаю"
        ANY = "*"

    class Sources(str, Enum):
        REMANGA = "remanga"
        SHIKIMORI = "shikimori"
        MANGA_POISK = "manga_poisk"

        def __str__(self):
            return self.value

    class Status:
        RELEASED = "Закончен"
        ONGOING = "Продолжается"
        FROZEN = "Заморожен"
        LICENSED = "Лицензировано"
        ANONS = "Анонс"
        NO_TRANSLATOR = "Нет переводчика"
        UNKNOWN = "Неизвестно"

    STATUSES = {
        Status.ONGOING: ["ongoing", "продолжается", "ONGOING", "2", "4"],
        Status.LICENSED: ["licensed", "лицензировано"],
        Status.RELEASED: ["released", "done", "закончен"],
        Status.FROZEN: ["frozen", "заморожен"],
        Status.ANONS: ["анонс"],
        Status.NO_TRANSLATOR: ["?"],
    }
