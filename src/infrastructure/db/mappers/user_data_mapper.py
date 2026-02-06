from src.infrastructure.db.models import UserDBModel
from src.domain.models.users import UserData


class UserDataMapper:
    """Mapper for converting between UserData (domain) and UserDBModel (database)."""

    @staticmethod
    def to_db(
        data: UserData,
        google_id: str | None = None,
        yandex_id: str | None = None,
    ) -> UserDBModel:
        """Convert UserData domain model to UserDBModel."""
        return UserDBModel(
            username=data.username,
            email=data.email,
            hashed_password=data.hashed_password,
            google_id=google_id,
            yandex_id=yandex_id,
            role=data.role,
            avatar_path=data.avatar_path,
            description=data.description,
            is_active=data.is_active,
            extended_data=data.extended_data,
        )

    @staticmethod
    def to_domain(data: UserDBModel) -> UserData:
        """Convert UserDBModel to UserData domain model."""
        return UserData(
            id=data.id,
            username=data.username,
            email=data.email,
            hashed_password=data.hashed_password,
            avatar_path=data.avatar_path,
            role=data.role,
            description=data.description,
            is_active=data.is_active,
            extended_data=data.extended_data,
        )
