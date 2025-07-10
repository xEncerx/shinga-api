from jinja2 import Environment, FileSystemLoader
from email.utils import formatdate, make_msgid
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any
import aiosmtplib
import asyncio

from app.core import settings, logger


class EmailService:
    """
    Email service for sending emails via SMTP.
    
    This service provides functionality for sending emails
    using Jinja2 templates for both HTML and text content.
    """
    _smtp_server = settings.SMTP_SERVER
    _smtp_port = settings.SMTP_PORT
    _smtp_username = settings.SMTP_USERNAME
    _smtp_password = settings.SMTP_PASSWORD
    _templates_dir = settings.CORE_PATH.parent.parent / "templates" / "emails"
    _env = Environment(loader=FileSystemLoader(_templates_dir))

    @classmethod
    async def send_password_reset_email(
        cls, recipient_email: str, reset_code: str
    ) -> bool:
        """
        Send a password reset email to the specified recipient.
        
        Args:
            recipient_email (str): The email address to send the reset code to
            reset_code (str): The password reset code to include in the email
            
        Returns:
            bool: True if email was sent successfully, False otherwise
        """
        try:
            msg = MIMEMultipart("alternative")
            msg["From"] = f"Shinga Support <{cls._smtp_username}>"
            msg["To"] = recipient_email
            msg["Subject"] = "Восстановление пароля - Shinga"
            msg["Date"] = formatdate(localtime=True)
            msg["Message-ID"] = make_msgid(domain="shinga.ru")

            html_body, text_body = cls._render_password_reset_email(reset_code)

            text_part = MIMEText(text_body, "plain", "utf-8")
            html_part = MIMEText(html_body, "html", "utf-8")

            msg.attach(text_part)
            msg.attach(html_part)

            return await cls.send_email(msg, recipient_email)

        except Exception as e:
            logger.error(f"Cant send reset password email: {e}")
            return False

    @classmethod
    async def send_email(cls, msg: MIMEMultipart, recipient_email: str) -> bool:
        """
        Send an email message via SMTP with retry logic.
        
        This method attempts to send the email up to 3 times with exponential
        backoff between attempts.
        
        Args:
            msg (MIMEMultipart): The email message to send
            recipient_email (str): The recipient's email address
            
        Returns:
            bool: True if email was sent successfully, False otherwise
        """
        max_retries = 3
        for attempt in range(max_retries):
            try:
                async with aiosmtplib.SMTP(
                    hostname=cls._smtp_server,
                    port=cls._smtp_port,
                    username=cls._smtp_username,
                    password=cls._smtp_password,
                    start_tls=True,
                    timeout=30,
                ) as server:
                    await server.sendmail(
                        cls._smtp_username, recipient_email, msg.as_string()
                    )
                return True
            except Exception as e:
                logger.warning(f"SMTP attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(2**attempt)
                else:
                    logger.error(f"SMTP error after {max_retries} attempts: {e}")
        return False

    @classmethod
    def _render_template(cls, template_name: str, context: dict[str, Any]) -> str:
        """
        Render a Jinja2 template with the given context.
        
        Args:
            template_name (str): Name of the template file to render
            context (dict[str, Any]): Variables to pass to the template
            
        Returns:
            str: The rendered template content
        """
        template = cls._env.get_template(template_name)
        return template.render(**context)

    @classmethod
    def _render_password_reset_email(cls, reset_code: str) -> tuple[str, str]:
        """
        Render both HTML and text versions of the password reset email.
        
        Args:
            reset_code (str): The password reset code to include in the templates
            
        Returns:
            tuple[str, str]: A tuple containing (html_content, text_content)
        """
        context = {"reset_code": reset_code}

        html_content = cls._render_template("password_reset.html", context)
        text_content = cls._render_template("password_reset.txt", context)

        return html_content, text_content