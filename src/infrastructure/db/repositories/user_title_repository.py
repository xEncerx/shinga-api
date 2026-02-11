from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, func, update, case

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

    async def get_user_title(self, user_id: int, title_id: int) -> UserTitleData | None:
        stmt = select(UserTitlesDBModel).where(
            UserTitlesDBModel.user_id == user_id,
            UserTitlesDBModel.title_id == title_id,
        )
        result = await self._session.exec(stmt)
        db_model = result.first()

        if db_model is None:
            return None

        return UserTitleMapper.to_domain(db_model)

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
        rows = result.all()

        ratings: dict[int, int] = {row.rating: row.count for row in rows}  # type: ignore

        total_ratings = sum(ratings.values())
        if total_ratings > 0:
            weighted_sum = sum(rating * count for rating, count in ratings.items())
            average_rating = weighted_sum / total_ratings
        else:
            average_rating = 0.0

        return RatingStatistics(
            average_rating=round(average_rating, 1),
            ratings_count=total_ratings,
            ratings_distribution=ratings,
        )
