from email.utils import formatdate, make_msgid
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import aiosmtplib

from src.domain.interfaces import IEmailService, EmailMessage
from src.domain.errors import EmailSendError

__all__ = ["SMTPEmailService"]


class SMTPEmailService(IEmailService):
    """SMTP implementation of email service"""

    def __init__(
        self,
        smtp_host: str,
        smtp_port: int,
        smtp_username: str,
        smtp_password: str,
        email_domain: str,
        use_tls: bool = True,
    ):
        """
        Initialize SMTP email service

        Args:
            smtp_host: SMTP server hostname
            smtp_port: SMTP server port
            smtp_username: SMTP authentication username
            smtp_password: SMTP authentication password
            use_tls: Whether to use TLS
        """
        self._smtp_host = smtp_host
        self._smtp_port = smtp_port
        self._smtp_username = smtp_username
        self._smtp_password = smtp_password
        self._email_domain = email_domain
        self._use_tls = use_tls

    async def send_email(self, message: EmailMessage) -> bool:
        """
        Send an email via SMTP

        Args:
            message: EmailMessage object containing email details

        Returns:
            bool: True if sent successfully

        Raises:
            EmailSendError: If sending fails
        """
        try:
            # Create message
            msg = MIMEMultipart("alternative")
            msg["Subject"] = message.subject
            msg["From"] = self._smtp_username
            msg["To"] = message.to
            msg["Date"] = formatdate(localtime=True)
            msg["Message-ID"] = make_msgid(domain=self._email_domain)

            # Add HTML body
            html_part = MIMEText(message.html_body, "html")
            msg.attach(html_part)

            # Send email
            async with aiosmtplib.SMTP(
                hostname=self._smtp_host,
                port=self._smtp_port,
                username=self._smtp_username,
                password=self._smtp_password,
                start_tls=self._use_tls,
                timeout=20,
            ) as smtp:
                await smtp.send_message(msg)

            return True

        except aiosmtplib.SMTPException as e:
            raise EmailSendError(f"Failed to send email: {str(e)}")
        except Exception as e:
            raise EmailSendError(f"Unexpected error: {str(e)}")
