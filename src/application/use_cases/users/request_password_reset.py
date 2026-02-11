from dataclasses import dataclass
from datetime import timedelta

from src.domain.interfaces import (
    IUserRepository,
    IVerificationCodeStorage,
    IEmailTemplateRenderer,
    ILocalizationService,
)
from src.application.tasks.email_tasks import send_email_task
from src.infrastructure.security import CodeGenerator
from src.domain.errors import UserNotFoundError
from src.domain.models import Language
from src.core import settings


class RequestPasswordResetUseCase:
    """Use case for initiating password reset process"""

    def __init__(
        self,
        user_repository: IUserRepository,
        code_storage: IVerificationCodeStorage,
        template_renderer: IEmailTemplateRenderer,
        localization_service: ILocalizationService,
        code_expiration: timedelta = timedelta(minutes=15),
    ):
        """
        Initialize use case

        Args:
            user_repository: Repository for user operations
            code_storage: Storage for verification codes
            template_renderer: Renderer for email templates
            localization_service: Service for localizing email content
            code_expiration: Expiration time for verification codes
        """
        self._user_repository = user_repository
        self._code_storage = code_storage
        self._template_renderer = template_renderer
        self._localization_service = localization_service
        self._code_expiration = code_expiration

    async def execute(self, email: str, language: Language = Language.RU) -> None:
        """
        Request password reset by sending verification code to email

        Args:
            email: User's email address

        Raises:
            UserNotFoundError: If user with email does not exist
        """
        # 1. Verify user exists
        user = await self._user_repository.get_by_email(email)
        if not user:
            raise UserNotFoundError(f"User with email <{email}> not found")

        # 2. Generate verification code
        code = CodeGenerator.generate_confirmation_code(length=6)

        # 3. Store code in Redis with expiration
        stored = await self._code_storage.store_code(
            key=email,
            code=code,
            expiration=self._code_expiration,
        )

        if not stored:
            raise Exception("Failed to store verification code")

        # 4. Get localized template name
        template_name = self._localization_service.get_template_name(
            "password_reset_ru.html",
            language,
        )

        # 5. Render email template
        html_body = self._template_renderer.render(
            template_name=template_name,
            context={
                "reset_code": code,
                "expiration_minutes": int(self._code_expiration.total_seconds() / 60),
                "app_name": settings.APP_NAME,
            },
        )

        # 6. Get localized subject
        subject = self._localization_service.get(
            "password_reset.subject",
            language,
            app_name=settings.APP_NAME,
        )

        # 7. Send email via task
        await send_email_task.kiq(
            to=email,
            subject=subject,
            html_body=html_body,
        )  # type: ignore
