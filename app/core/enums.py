from enum import Enum

class Language(str, Enum):
    EN = "en"
    RU = "ru"

    @property
    def full(self) -> str:
        return {
            Language.EN: "English",
            Language.RU: "Русский"
        }[self]
    
class TranslatorProvider(str, Enum):
    GOOGLE = "google"
    OPENAI = "openai"