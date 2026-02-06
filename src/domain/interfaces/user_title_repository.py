from abc import ABC, abstractmethod

from src.domain.models.users import (
    BookmarkStatistics,
    RatingStatistics,
    UserTitleData,
    UserTitleDataUpdate,
)


class IUserTitleRepository(ABC):
    @abstractmethod
    async def exists(self, user_id: int, title_id: int) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def add_user_title(
        self,
        user_id: int,
        title_id: int,
        data: UserTitleData,
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    async def update_user_title(
        self,
        user_id: int,
        title_id: int,
        data: UserTitleDataUpdate,
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    async def get_bookmark_statistics(self, user_id: int) -> BookmarkStatistics:
        raise NotImplementedError

    @abstractmethod
    async def get_rating_statistics(self, user_id: int) -> RatingStatistics:
        raise NotImplementedError
