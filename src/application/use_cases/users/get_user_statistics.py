from src.domain.interfaces import IUserTitleRepository
from src.domain.models.users import UserStatistics

__all__ = ["GetUserStatisticsUseCase"]


class GetUserStatisticsUseCase:
    def __init__(self, user_title_repository: IUserTitleRepository):
        self._user_title_repository = user_title_repository

    async def execute(self, user_id: int) -> UserStatistics:
        bookmarks = await self._user_title_repository.get_bookmark_statistics(user_id)
        ratings = await self._user_title_repository.get_rating_statistics(user_id)

        return UserStatistics(bookmarks=bookmarks, ratings=ratings)
