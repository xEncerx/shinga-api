from src.domain.interfaces import IUserTitleRepository, ITitleRepository
from src.domain.models.users import UserTitleData
from src.domain.errors import RecordNotFoundError, RecordAlreadyExistsError

__all__ = ["AddUserTitleUseCase"]


class AddUserTitleUseCase:
    """Use case for adding a user title."""

    def __init__(
        self,
        user_title_repository: IUserTitleRepository,
        title_repository: ITitleRepository,
    ) -> None:
        self._user_title_repository = user_title_repository
        self._title_repository = title_repository

    async def execute(self, user_id: int, title_id: int, data: UserTitleData) -> None:
        """
        Executes the use case to add a user title.

        Args:
            user_id (int): The ID of the user.
            title_id (int): The ID of the title to add.
            data (UserTitleData): The data to add the user title with.

        Raises:
            RecordNotFoundError: If the master title does not exist.
            RecordAlreadyExistsError: If the user title already exists.
        """
        # Ensure the title exists before adding the user title
        result = await self._title_repository.get_master_title(title_id)
        if result is None:
            raise RecordNotFoundError(details=[f"Title with ID {title_id} not found."])

        result = await self._user_title_repository.exists(user_id, title_id)
        if result:
            raise RecordAlreadyExistsError(details=[f"User title already exists."])

        await self._user_title_repository.add_user_title(user_id, title_id, data)
