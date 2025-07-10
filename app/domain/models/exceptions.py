class DomainException(Exception):
    """Base class for domain exceptions."""
    message: str = "Domain error"

    def __init__(self, message: str | None = None):
        self.message = message or self.message

        super().__init__(self.message)

# --- User exceptions ---
class UserAlreadyExistsError(DomainException):
    message = "User already exists"

class UserNotFoundError(DomainException):
    message = "User not found"

class InvalidCredentialsError(DomainException):
    message = "Invalid credentials"