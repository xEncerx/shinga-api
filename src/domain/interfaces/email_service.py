from abc import ABC, abstractmethod
from dataclasses import dataclass

__all__ = ["IEmailService", "IEmailTemplateRenderer", "EmailMessage"]


@dataclass(frozen=True)
class EmailMessage:
    """Data class representing an email message"""

    to: str
    subject: str
    html_body: str


class IEmailService(ABC):
    """Interface for email sending operations"""

    @abstractmethod
    async def send_email(self, message: EmailMessage) -> bool:
        """
        Send an email message

        Args:
            message: EmailMessage object containing all email details

        Returns:
            bool: True if email was sent successfully, False otherwise
        """
        pass


class IEmailTemplateRenderer(ABC):
    """Interface for rendering email templates"""

    @abstractmethod
    def render(self, template_name: str, context: dict) -> str:
        """
        Render an email template with given context

        Args:
            template_name: Name of the template file
            context: Dictionary with template variables

        Returns:
            str: Rendered HTML string
        """
        pass
