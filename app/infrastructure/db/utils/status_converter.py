from ..models.title.relations import TitleStatus

class StatusConverter:
    """Utility class for converting title statuses between different formats."""
    @staticmethod
    def from_shiki(shiki_status: str) -> TitleStatus:
        """Converts a Shikimori status string to a TitleStatus enum."""
        mapping = {
            "ongoing": TitleStatus.ONGOING,
            "released": TitleStatus.FINISHED,
            "discontinued": TitleStatus.DISCONTINUED,
            "paused": TitleStatus.FROZEN,
            "anons": TitleStatus.ANONS,
        }
        return mapping.get(shiki_status.lower(), TitleStatus.UNKNOWN)
    
    @staticmethod
    def to_shiki(status: TitleStatus) -> str:
        raise NotImplementedError("Shiki status conversion is not implemented yet.")
    
    @staticmethod
    def from_mal(mal_status: str) -> TitleStatus:
        """Converts a MyAnimeList status string to a TitleStatus enum."""
        mapping = {
            "publishing": TitleStatus.ONGOING,
            "finished": TitleStatus.FINISHED,
            "discontinued": TitleStatus.DISCONTINUED,
            "on hiatus": TitleStatus.FROZEN,
            "upcoming": TitleStatus.ANONS,
        }
        return mapping.get(mal_status.lower(), TitleStatus.UNKNOWN)
    
    @staticmethod
    def to_mal(status: TitleStatus) -> str:
        raise NotImplementedError("MAL status conversion is not implemented yet.")
    
    @staticmethod
    def from_remanga(remanga_status: str) -> TitleStatus:
        """Converts a Remanga status string to a TitleStatus enum."""
        mapping = {
            "Закончен": TitleStatus.FINISHED,
            "Продолжается": TitleStatus.ONGOING,
            "Заморожен": TitleStatus.FROZEN,
            "Лицензировано": TitleStatus.LICENSED,
            "Анонс": TitleStatus.ANONS,
        }
        return mapping.get(remanga_status, TitleStatus.UNKNOWN)
    
    @staticmethod
    def to_remanga(status: TitleStatus) -> str:
        raise NotImplementedError("Remanga status conversion is not implemented yet.")