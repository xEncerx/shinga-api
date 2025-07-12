from fastapi.responses import RedirectResponse
from fastapi import APIRouter

from app.domain.models.exceptions import UserAlreadyExistsError
from ...schemas import Token, OAuthError, UserAlreadyExists
from app.infrastructure.db.crud.user import get_user
from app.core.security import create_access_token
from app.domain.use_cases import create_user
from app.core.oauth import *
from app.core import logger

router = APIRouter(prefix=f"/yandex")


@router.get("/login")
async def login() -> RedirectResponse:
    """
    Initiates the Yandex OAuth login process.

    Returns:
        RedirectResponse: Redirects to the Yandex OAuth authorization URL.
    """
    authorization_url = await yandex_oauth.get_authorization_url(
        redirect_uri=settings.YANDEX_REDIRECT_URI
    )
    return RedirectResponse(authorization_url)


@router.get("/callback", response_model=Token)
async def auth_callback(access_token_state=YandexCallbackDep):
    """
    Yandex OAuth callback endpoint.

    Returns:
        Token: A token containing the access token for the authenticated user.

    Raises:
        OAuthError: If the access token is not found or if the user profile does not contain an email address.
        UserAlreadyExists: If a user with the same Yandex ID already exists.
    """
    token, _ = access_token_state
    if "access_token" not in token:
        raise OAuthError(detail="Access token not found in the response.")

    yandex_data = await yandex_oauth.get_profile(token=token["access_token"])

    if not yandex_data.email:
        raise OAuthError(
            detail="Yandex OAuth profile does not contain an email address."
        )

    user = await get_user(yandex_id=yandex_data.id)
    if not user:
        try:
            user = await create_user(
                username=yandex_data.email,
                email=yandex_data.email,
                yandex_id=yandex_data.id,
            )
        except UserAlreadyExistsError as e:
            raise UserAlreadyExists(detail=e.message)
        except Exception as e:
            logger.error(f"Failed to create user: {e}")
            raise OAuthError(detail="Failed to create user from Yandex profile.")

    return Token(access_token=create_access_token(subject=user.id))  # type: ignore
