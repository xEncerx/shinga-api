from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select

from app.models import User, UserCreate, UserUpdate
from app.core.security import *


async def create_user(
    *,
    session: AsyncSession,
    user_create: UserCreate,
) -> User:
    """
    Create a new user in the database.
    Args:
        session (AsyncSession): The database session used for the transaction.
        user_create (UserCreate): The user data for creating a new user.
    Returns:
        User: The newly created user object with updated database information.
    Note:
        The password from user_create is hashed before storage, and a recovery code
        is automatically generated for the user.
    """
    db_obj = User.model_validate(
        user_create,
        update={
            "hashed_password": get_password_hash(user_create.password),
            "recovery_code": generate_recovery_code(),
        },
    )

    session.add(db_obj)
    await session.commit()
    await session.refresh(db_obj)

    return db_obj


async def update_user(
    *,
    session: AsyncSession,
    db_user: User,
    user_in: UserUpdate,
) -> User:
    """
    Update a user in the database.
    Args:
        session (AsyncSession): The database session to use for the operation.
        db_user (User): The database user object to update.
        user_in (UserUpdate): The input data containing user information to update.
    Returns:
        User: The updated user object.
    """
    user_data = user_in.model_dump(exclude_unset=True)
    extra_data = {}

    if "password" in user_data:
        password = user_data["password"]
        hashed_password = get_password_hash(password)
        extra_data["hashed_password"] = hashed_password

    db_user.sqlmodel_update(user_data, update=extra_data)
    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)

    return db_user


async def get_user(*, session: AsyncSession, username: str) -> User | None:
    """
    Get a user by username.
    Args:
        session (AsyncSession): The database session for executing the query.
        username (str): The username to search for.
    Returns:
        User | None: The found user object or None if no user with the given username exists.
    """
    statement = select(User).where(User.username.ilike(username))
    user = (await session.exec(statement)).first()

    return user


async def authenticate(
    *,
    session: AsyncSession,
    username: str,
    password: str,
) -> User | None:
    """
    Authenticate a user with the given username and password.
    Args:
        session (AsyncSession): The database session.
        username (str): The username to authenticate.
        password (str): The plain-text password to verify.
    Returns:
        User | None: The authenticated User object if the credentials are valid, None otherwise.
    """
    user = await get_user(session=session, username=username)

    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None

    return user
