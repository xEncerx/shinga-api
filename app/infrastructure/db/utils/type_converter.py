from ..models.title.relations import TitleType

class TypeConverter:
    @staticmethod
    def from_shiki(shiki_status: str) -> TitleType:
        """Converts Shikimori title type string to TitleType enum."""
        mapping = {
            "manga": TitleType.MANGA,
            "manhwa": TitleType.MANHWA,
            "manhua": TitleType.MANHUA,
            "light_novel": TitleType.LIGHT_NOVEL,
            "novel": TitleType.NOVEL,
            "one_shot": TitleType.ONESHOT,
            "doujin": TitleType.DOUJIN,
        }
        return mapping.get(shiki_status.lower(), TitleType.OTHER)
    
    @staticmethod
    def to_shiki(type_: TitleType) -> str:
        raise NotImplementedError("Conversion to Shikimori type is not implemented yet.")
    
    @staticmethod
    def from_mal(mal_status: str) -> TitleType:
        """Converts a MyAnimeList title type string to a TitleType enum."""
        mapping = {
            "manga": TitleType.MANGA,
            "manhwa": TitleType.MANHWA,
            "manhua": TitleType.MANHUA,
            "light novel": TitleType.LIGHT_NOVEL,
            "novel": TitleType.NOVEL,
            "one-shot": TitleType.ONESHOT,
            "doujinshi": TitleType.DOUJIN,
            "webtoon": TitleType.WEBTOON,
        }
        return mapping.get(mal_status.lower(), TitleType.OTHER)
    
    @staticmethod
    def to_mal(type_: TitleType) -> str:
        raise NotImplementedError("Conversion to MyAnimeList type is not implemented yet.")
    
    @staticmethod
    def from_remanga(remanga_status: str) -> TitleType:
        """Converts a Remanga title type string to a TitleType enum."""
        mapping = {
            "Другое": TitleType.OTHER,
            "Манга": TitleType.MANGA,
            "Манхва": TitleType.MANHWA,
            "Маньхуа": TitleType.MANHUA,
            "Западный комикс": TitleType.COMICS,
            "Рукомикс": TitleType.COMICS,
        }
        return mapping.get(remanga_status, TitleType.OTHER)
    
    @staticmethod
    def to_remanga(type_: TitleType) -> str:
        raise NotImplementedError("Conversion to Remanga type is not implemented yet.")