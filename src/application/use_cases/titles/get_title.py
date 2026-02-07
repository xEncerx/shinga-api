from dataclasses import dataclass

from src.domain.interfaces import ITitleRepository, IUserTitleRepository
from src.domain.errors.database import RecordNotFoundError
from src.domain.models import TitleData, UserTitleData

__all__ = ["GetTitleUseCase"]


@dataclass(frozen=True)
class GetTitleResult:
    title: TitleData
    user_data: UserTitleData | None


class GetTitleUseCase:
    """Use case for retrieving a title by its ID."""

    def __init__(
        self,
        user_title_repository: IUserTitleRepository,
        title_repository: ITitleRepository,
    ) -> None:
        self._user_title_repository = user_title_repository
        self._title_repository = title_repository

    async def execute(
        self, title_id: int, user_id: int | None = None
    ) -> GetTitleResult:
        """
        Retrieve a title by its ID with optional user-specific data.

        Args:
            title_id (int): The ID of the title to retrieve.
            user_id (int | None): The ID of the user, if authenticated.

        Returns:
            GetTitleResult: Title data with optional user-specific data.

        Raises:
            RecordNotFoundError: If no title with the given ID is found.
        """
        title = await self._title_repository.get_master_title(title_id)
        if title is None:
            raise RecordNotFoundError([f"Title with id {title_id} not found"])

        user_title_data = None
        if user_id is not None:
            user_title_data = await self._user_title_repository.get_user_title(
                user_id, title_id
            )

        return GetTitleResult(title=title, user_data=user_title_data)
