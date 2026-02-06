import secrets
import string


class CodeGenerator:
    """Service for generating random values"""

    @staticmethod
    def generate_random_string(length: int = 32) -> str:
        return secrets.token_urlsafe(length)

    @staticmethod
    def generate_confirmation_code(length: int = 6) -> str:
        return "".join(secrets.choice(string.digits) for _ in range(length))

    @staticmethod
    def generate_random_password(length: int = 12) -> str:
        alphabet = string.ascii_letters + string.digits + string.punctuation
        return "".join(secrets.choice(alphabet) for _ in range(length))
