from src.domain.models.users import UserTitleData, UserTitleDataUpdate
from src.infrastructure.db.models import UserTitlesDBModel

__all__ = ["UserTitleMapper"]


class UserTitleMapper:
    @staticmethod
    def to_db(
        user_id: int,
        title_id: int,
        data: UserTitleData,
    ) -> UserTitlesDBModel:
        return UserTitlesDBModel(
            user_id=user_id,
            title_id=title_id,
            rating=data.rating,
            current_url=data.current_url,
            bookmark=data.bookmark,
            is_favorite=data.is_favorite,
            extended_data=data.extended_data,
        )

    @staticmethod
    def to_domain(data: UserTitlesDBModel) -> UserTitleData:
        return UserTitleData(
            rating=data.rating,
            current_url=data.current_url,
            bookmark=data.bookmark,
            is_favorite=data.is_favorite,
            extended_data=data.extended_data,
        )
