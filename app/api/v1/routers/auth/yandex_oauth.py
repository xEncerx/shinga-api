from fastapi.responses import RedirectResponse
from fastapi import APIRouter, Request, Query

from app.domain.models.exceptions import UserAlreadyExistsError
from ...schemas import Token, OAuthError, UserAlreadyExists
from app.infrastructure.db.crud import UserCRUD
from app.domain.use_cases import create_user
from app.core import logger, limiter
from app.core.security import *
from app.core.oauth import *

router = APIRouter(prefix=f"/yandex")


@router.get("/login")
@limiter.limit("5/minute")
async def login(request: Request) -> RedirectResponse:
    """
    Initiates the Yandex OAuth login process.

    **Limits: 5 requests per minute**

    Returns:
        RedirectResponse: Redirects to the Yandex OAuth authorization URL.
    """
    authorization_url = await yandex_oauth.get_authorization_url(
        redirect_uri=settings.YANDEX_REDIRECT_URI
    )
    return RedirectResponse(authorization_url)


@router.post("/exchange")
@limiter.limit("5/minute")
async def exchange_token(access_token: str = Query(...), *, request: Request):
    yandex_data = await yandex_oauth.get_profile(token=access_token)

    if not yandex_data.email:
        raise OAuthError(
            detail="Yandex OAuth profile does not contain an email address."
        )

    user = await UserCRUD.read.user(yandex_id=yandex_data.id)
    if not user:
        try:
            user = await create_user(
                username=generate_random_string(),
                email=yandex_data.email,
                yandex_id=yandex_data.id,
            )
        except UserAlreadyExistsError as e:
            raise UserAlreadyExists(detail=e.message)
        except Exception as e:
            logger.error(f"Failed to create user: {e}")
            raise OAuthError(detail="Failed to create user from Yandex profile.")

    return Token(access_token=create_access_token(subject=user.id))  # type: ignore


@router.get("/callback", response_model=Token)
@limiter.limit("5/minute")
async def auth_callback(access_token_state=YandexCallbackDep, *, request: Request):
    """
    Yandex OAuth callback endpoint.

    **Limits: 5 requests per minute**

    Returns:
        Token: A token containing the access token for the authenticated user.

    Raises:
        OAuthError: If the access token is not found or if the user profile does not contain an email address.
        UserAlreadyExists: If a user with the same Yandex ID already exists.
    """
    token, _ = access_token_state
    if "access_token" not in token:
        raise OAuthError(detail="Access token not found in the response.")

    await exchange_token(
        access_token=token["access_token"],
        request=request
    )
