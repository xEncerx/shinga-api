from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, func, update

from src.infrastructure.db.models import UserTitlesDBModel
from src.infrastructure.db.mappers import UserTitleMapper
from src.domain.models.users import (
    BookmarkStatistics,
    RatingStatistics,
    UserTitleData,
    UserTitleDataUpdate,
)
from src.domain.interfaces import IUserTitleRepository


class UserTitleRepository(IUserTitleRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def exists(self, user_id: int, title_id: int) -> bool:
        stmt = select(UserTitlesDBModel).where(
            UserTitlesDBModel.user_id == user_id,
            UserTitlesDBModel.title_id == title_id,
        )
        result = await self._session.exec(stmt)
        return result.first() is not None

    async def add_user_title(
        self,
        user_id: int,
        title_id: int,
        data: UserTitleData,
    ) -> None:
        db_model = UserTitleMapper.to_db(user_id, title_id, data)
        self._session.add(db_model)
        await self._session.flush()

    async def update_user_title(
        self,
        user_id: int,
        title_id: int,
        data: UserTitleDataUpdate,
    ) -> None:
        update_data = data.model_dump(exclude_none=True)

        if not update_data:
            return

        stmt = (
            update(UserTitlesDBModel)
            .where(
                UserTitlesDBModel.user_id == user_id,  # type: ignore
                UserTitlesDBModel.title_id == title_id,  # type: ignore
            )
            .values(**update_data)
        )

        await self._session.exec(stmt)
        await self._session.flush()

    async def get_bookmark_statistics(self, user_id: int) -> BookmarkStatistics:
        stmt = (
            select(
                UserTitlesDBModel.bookmark,  # type: ignore
                func.count().label("count"),
            )
            .where(UserTitlesDBModel.user_id == user_id)
            .group_by(UserTitlesDBModel.bookmark)
        )

        result = await self._session.exec(stmt)
        bookmarks = {row.bookmark: row.count for row in result.all()}  # type: ignore

        return BookmarkStatistics(
            bookmarks=bookmarks,  # type: ignore
            total=sum(bookmarks.values()),  # type: ignore
        )

    async def get_rating_statistics(self, user_id: int) -> RatingStatistics:
        stmt = (
            select(
                func.count(
                    case((UserTitlesDBModel.rating > 0, 1)),  # type: ignore
                ).label("rated_count"),
                func.avg(UserTitlesDBModel.rating).label("avg_rating"),
                UserTitlesDBModel.rating,
                func.count().label("count"),
            )
            .where(
                UserTitlesDBModel.user_id == user_id,
                UserTitlesDBModel.rating > 0,
            )
            .group_by(UserTitlesDBModel.rating)  # type: ignore
        )

        result = await self._session.exec(stmt)
        ratings: dict[int, int] = {row.rating: row.count for row in result.all()}  # type: ignore

        return RatingStatistics(
            average_rating=result.first().avg_rating if result.first() else 0.0,  # type: ignore
            ratings_count=result.first().rated_count if result.first() else 0,  # type: ignore
            ratings_distribution=ratings,
        )
