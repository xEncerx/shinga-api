from sqlmodel import Session, select

from app.models import Users, UserCreate, UserUpdate
from app.core.security import *


def create_user(*, session: Session, user_create: UserCreate) -> Users:
    """
    Create a new user in the database.
    Args:
            session (Session): The database session.
            user_create (UserCreate): The user data for creation.
    Returns:
            Users: The created user object with all fields populated from the database.
    Note:
            This function hashes the provided password and generates a recovery code
            before storing the user in the database.
    """

    db_obj = Users.model_validate(
        user_create,
        update={
            "hashed_password": get_password_hash(user_create.password),
            "recovery_code": generate_recovery_code(),
        },
    )

    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)

    return db_obj


def update_user(
    *,
    session: Session,
    db_user: Users,
    user_in: UserUpdate,
) -> Any:
    """
    Update a user in the database with new data.
    Args:
            session: The database session.
            db_user: The database user model instance to update.
            user_in: The input data for updating the user.
    Returns:
            The updated user object.
    Notes:
            - If a password is provided in the input data, it will be hashed before storing.
            - The function updates the user in the database, commits the changes, and refreshes the user object.
    """

    user_data = user_in.model_dump(exclude_unset=True)
    extra_data = {}

    if "password" in user_data:
        password = user_data["password"]
        hashed_password = get_password_hash(password)
        extra_data["hashed_password"] = hashed_password

    db_user.sqlmodel_update(user_data, update=extra_data)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    return db_user


def get_user(*, session: Session, username: str) -> Users | None:
    """
    Retrieve a user from the database by username.

    This function queries the database to find a user with the specified username.

    Args:
            session (Session): The database session to use for the query.
            username (str): The username to search for.

    Returns:
            Users | None: The user object if found, None otherwise.
    """

    statement = select(Users).where(Users.username == username)
    user = session.exec(statement).first()
    return user


def authenticate(
    *,
    session: Session,
    username: str,
    password: str,
) -> Users | None:
    """
    Authenticate a user with the provided username and password.

    Args:
            session (Session): The database session.
            username (str): The username of the user trying to authenticate.
            password (str): The plaintext password for verification.

    Returns:
            Users | None: The user object if authentication is successful, None otherwise.
                    Authentication fails if the user doesn't exist or if the password is incorrect.
    """

    user = get_user(session=session, username=username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user
