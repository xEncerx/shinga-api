from abc import ABC, abstractmethod
from src.domain.models.language import Language

__all__ = ["ILocalizationService"]


class ILocalizationService(ABC):
    """Interface for localization service"""

    @abstractmethod
    def get(self, key: str, language: Language, **kwargs) -> str:
        """
        Get localized string by key

        Args:
            key: Translation key
            language: Target language
            **kwargs: Variables for string formatting

        Returns:
            Localized string
        """
        pass

    @abstractmethod
    def get_template_name(self, base_template: str, language: Language) -> str:
        """
        Get template name for specified language

        Args:
            base_template: Base template name (e.g., 'password_reset.html')
            language: Target language

        Returns:
            Localized template name
        """
        pass
