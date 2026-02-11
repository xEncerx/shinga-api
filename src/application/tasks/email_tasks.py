from taskiq import Context, TaskiqDepends
from typing import Annotated

from src.infrastructure.tasks.broker import broker
from src.domain.interfaces import EmailMessage
from src.domain.errors import EmailSendError
from src.core import logger


__all__ = ["send_email_task"]


@broker.task(retry_on_error=True, max_retries=3)
async def send_email_task(
    to: str,
    subject: str,
    html_body: str,
    *,
    context: Annotated[Context, TaskiqDepends()],
):
    """
    Task: Send an email message with retry logic

    Args:
        to: Recipient email address
        subject: Email subject
        html_body: HTML body of the email
        context: Taskiq context with email service dependency

    Raises:
        EmailSendError: If sending fails after retries
    """
    try:
        email_service = context.state.email_service
        message = EmailMessage(
            to=to,
            subject=subject,
            html_body=html_body,
        )

        await email_service.send_email(message)

        logger.info(f"Email sent successfully to {to} with subject: {subject}")

    except EmailSendError as e:
        logger.error(f"Failed to send email to {to}: {e}")
        raise  # Re-raise to trigger retry
    except Exception as e:
        logger.error(f"Unexpected error sending email to {to}: {e}")
        raise EmailSendError(f"Unexpected error: {str(e)}")
