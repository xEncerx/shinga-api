from src.domain.interfaces import IUserTitleRepository, ITitleRepository
from src.domain.errors.database import RecordNotFoundError
from src.domain.models.users import UserTitleDataUpdate

__all__ = ["UpdateUserTitleUseCase"]


class UpdateUserTitleUseCase:
    """Use case for updating a user title."""

    def __init__(
        self,
        user_title_repository: IUserTitleRepository,
        title_repository: ITitleRepository,
    ) -> None:
        self._user_title_repository = user_title_repository
        self._title_repository = title_repository

    async def execute(
        self,
        user_id: int,
        title_id: int,
        data: UserTitleDataUpdate,
    ) -> None:
        """
        Executes the use case to update a user title.

        Args:
            user_id (int): The ID of the user.
            title_id (int): The ID of the title to update.
            data (UserTitleDataUpdate): The data to update the user title with.

        Raises:
            RecordNotFoundError: If the user title does not exist.
        """
        result = await self._user_title_repository.exists(user_id, title_id)
        if not result:
            raise RecordNotFoundError(
                details=[
                    f"The user title does not exist. Please add it first before updating."
                ]
            )

        await self._user_title_repository.update_user_title(user_id, title_id, data)
