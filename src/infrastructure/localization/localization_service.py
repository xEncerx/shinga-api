from src.domain.interfaces.localization import ILocalizationService
from src.domain.models import Language

__all__ = ["LocalizationService"]


class LocalizationService(ILocalizationService):
    """Service for managing application translations"""

    def __init__(self):
        """Initialize localization service with translations"""
        self._translations = {
            # Password reset translations
            "password_reset.subject": {
                Language.RU: "Восстановление пароля - {app_name}",
                Language.EN: "Password Reset - {app_name}",
            },
            "password_reset.email_title": {
                Language.RU: "Восстановление пароля",
                Language.EN: "Password Reset",
            },
        }

    def get(self, key: str, language: Language, **kwargs) -> str:
        if key not in self._translations:
            raise KeyError(f"Translation key '{key}' not found")

        if language not in self._translations[key]:
            language = Language.default()

        template = self._translations[key][language]
        return template.format(**kwargs) if kwargs else template

    def get_template_name(self, base_template: str, language: Language) -> str:
        """
        Get template name for specified language

        Args:
            base_template: Base template name (e.g., 'password_reset.html')
            language: Target language

        Returns:
            Localized template name (e.g., 'password_reset_en.html' or 'password_reset_ru.html')
        """
        if language == Language.RU:
            # Russian is the default, no suffix needed
            return base_template

        # Split filename and extension
        name, ext = base_template.rsplit(".", 1)
        return f"{name}_{language.value}.{ext}"
