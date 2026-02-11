from dataclasses import dataclass

from src.domain.interfaces import (
    IUserRepository,
    IVerificationCodeStorage,
    IPasswordHasher,
    IDataValidator,
)
from src.domain.errors import (
    UserNotFoundError,
    ValidationError,
    InvalidVerificationCodeError,
)


class ResetPasswordUseCase:
    """Use case for resetting user password with verification code"""

    def __init__(
        self,
        user_repository: IUserRepository,
        code_storage: IVerificationCodeStorage,
        password_hasher: IPasswordHasher,
        password_validator: IDataValidator,
    ):
        """
        Initialize use case

        Args:
            user_repository: Repository for user operations
            code_storage: Storage for verification codes
            password_hasher: Service for password hashing
            password_validator: Validator for password requirements
        """
        self._user_repository = user_repository
        self._code_storage = code_storage
        self._password_hasher = password_hasher
        self._password_validator = password_validator

    async def execute(self, email: str, code: str, new_password: str) -> None:
        """
        Reset user password after verifying code

        Args:
            email: User's email address
            code: Verification code
            new_password: New password to set

        Raises:
            UserNotFoundError: If user does not exist
            ValidationError: If password doesn't meet requirements
            InvalidVerificationCodeError: If code is invalid or expired
        """
        # 1. Validate new password
        is_valid, errors = self._password_validator.validate(new_password)
        if not is_valid:
            raise ValidationError(errors)

        # 2. Verify code and delete it atomically
        verified = await self._code_storage.verify_and_delete(email, code)
        if not verified:
            raise InvalidVerificationCodeError("Invalid or expired verification code")

        # 3. Get user
        user = await self._user_repository.get_by_email(email)
        if not user:
            raise UserNotFoundError(f"User with email <{email}> not found")

        # 4. Hash new password
        hashed_password = self._password_hasher.hash_password(new_password)

        # 5. Update user password
        await self._user_repository.update_password(user.id, hashed_password)  # type: ignore
