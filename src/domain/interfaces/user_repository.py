from abc import ABC, abstractmethod

from src.domain.models.users import UserData


class IUserRepository(ABC):
    @abstractmethod
    async def add_user(
        self,
        user_data: UserData,
        google_id: str | None = None,
        yandex_id: str | None = None,
    ) -> int:
        """Add a new user to the database."""
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, user_id: int) -> UserData | None:
        """Retrieve a user by their ID."""
        raise NotImplementedError

    @abstractmethod
    async def get_by_email(self, email: str) -> UserData | None:
        """Retrieve a user by their email."""
        raise NotImplementedError

    @abstractmethod
    async def get_by_username(self, username: str) -> UserData | None:
        """Retrieve a user by their username."""
        raise NotImplementedError
