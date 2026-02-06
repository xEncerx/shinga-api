from src.domain.interfaces import IDataValidator

import re

FORBIDDEN_PHRASES = [
    "admin",
    "administrator",
    "root",
    "moderator",
    "mod",
    "system",
    "support",
    "help",
    "null",
    "undefined",
    "test",
    "official",
    "staff",
    "none",
]


class UsernameValidator(IDataValidator):
    """
    A service class for validating usernames based on defined criteria.
    """

    def __init__(
        self,
        min_length=3,
        max_length=30,
        allow_special_char=False,
    ):
        self.min_length = min_length
        self.max_length = max_length
        self.allow_special_char = allow_special_char

    def validate(self, username: str) -> tuple[bool, list[str]]:
        """
        Validate the given username against the defined criteria.

        Args:
            username (str): The username string to validate.

        Returns:
            A boolean indicating if the username is valid, and a list of error messages.
        """
        errors = []

        if len(username) < self.min_length:
            errors.append(
                f"Username must be at least {self.min_length} characters long."
            )

        if len(username) > self.max_length:
            errors.append(
                f"Username must be at most {self.max_length} characters long."
            )

        if not re.match(r"^[a-zA-Z0-9._-]+$", username):
            errors.append(
                "Username must contain only English letters, digits, dots, underscores, and hyphens."
            )

        username_lower = username.lower()
        for phrase in FORBIDDEN_PHRASES:
            if phrase in username_lower:
                errors.append(f"Username cannot contain forbidden phrase.")
                break

        is_valid = len(errors) == 0
        return is_valid, errors
