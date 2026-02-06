from src.domain.interfaces import IDataValidator


class PasswordValidator(IDataValidator):
    """
    A service class for validating passwords based on defined criteria.
    """

    def __init__(
        self,
        min_length=8,
        require_special_char=True,
        require_numbers=True,
    ):
        self.min_length = min_length
        self.require_special_char = require_special_char
        self.require_numbers = require_numbers

    def validate(self, password: str) -> tuple[bool, list[str]]:
        """
        Validate the given password against the defined criteria.

        Args:
            password (str): The password string to validate.

        Returns:
            A boolean indicating if the password is valid, and a list of error messages.
        """
        errors = []

        if len(password) < self.min_length:
            errors.append(
                f"Password must be at least {self.min_length} characters long."
            )

        if self.require_special_char and not any(
            char in "!@#$%^&*()-_=+[]{}|;:'\",.<>?/`~" for char in password
        ):
            errors.append("Password must contain at least one special character.")

        if self.require_numbers and not any(char.isdigit() for char in password):
            errors.append("Password must contain at least one number.")

        is_valid = len(errors) == 0
        return is_valid, errors
