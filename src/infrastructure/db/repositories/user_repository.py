from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, func

from src.infrastructure.db.mappers import UserDataMapper
from src.infrastructure.db.models import UserDBModel
from src.domain.interfaces import IUserRepository
from src.domain.models.users import UserData


class UserRepository(IUserRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add_user(
        self,
        user_data: UserData,
        google_id: str | None = None,
        yandex_id: str | None = None,
    ) -> int:
        user = UserDataMapper.to_db(
            user_data,
            google_id=google_id,
            yandex_id=yandex_id,
        )
        self._session.add(user)
        await self._session.flush()
        await self._session.refresh(user)

        return user.id  # type: ignore

    async def get_by_id(self, user_id: int) -> UserData | None:
        user = await self._session.get(UserDBModel, user_id)
        if user is None:
            return None

        return UserDataMapper.to_domain(user)

    async def get_by_email(self, email: str) -> UserData | None:
        stmt = select(UserDBModel).where(UserDBModel.email == email)
        result = await self._session.exec(stmt)
        user = result.first()

        if user is None:
            return None

        return UserDataMapper.to_domain(user)

    async def get_by_username(self, username: str) -> UserData | None:
        stmt = select(UserDBModel).where(
            func.lower(UserDBModel.username) == username.lower()
        )
        result = await self._session.exec(stmt)
        user = result.first()

        if user is None:
            return None

        return UserDataMapper.to_domain(user)
