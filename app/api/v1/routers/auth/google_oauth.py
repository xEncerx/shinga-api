from fastapi.responses import RedirectResponse
from fastapi import APIRouter, Request

from app.domain.models.exceptions import UserAlreadyExistsError
from ...schemas import Token, OAuthError, UserAlreadyExists
from app.infrastructure.db.crud import UserCRUD
from app.domain.use_cases import create_user
from app.core import logger, limiter
from app.core.security import *
from app.core.oauth import *

router = APIRouter(prefix=f"/google")


@router.get("/login")
@limiter.limit("5/minute")
async def login(request: Request) -> RedirectResponse:
    """
    Initiates the Google OAuth login process.

    **Limits: 5 requests per minute**

    Returns:
        RedirectResponse: Redirects to the Google OAuth authorization URL.
    """
    authorization_url = await google_oauth.get_authorization_url(
        redirect_uri=settings.GOOGLE_REDIRECT_URI
    )
    return RedirectResponse(authorization_url)


@router.get("/callback", response_model=Token)
@limiter.limit("5/minute")
async def auth_callback(
    access_token_state=GoogleCallbackDep,
    *,
    request: Request
):
    """
    Google OAuth callback endpoint.

    **Limits: 5 requests per minute**

    Returns:
        Token: A token containing the access token for the authenticated user.

    Raises:
        OAuthError: If the access token is not found or if the user profile does not contain an email address.
        UserAlreadyExists: If a user with the same Google ID already exists.
    """
    token, _ = access_token_state
    if "access_token" not in token:
        raise OAuthError(detail="Access token not found in the response.")

    google_data = await google_oauth.get_profile(token=token["access_token"])

    if not google_data.email:
        raise OAuthError(
            detail="Google OAuth profile does not contain an email address."
        )

    user = await UserCRUD.read.user(google_id=google_data.id)
    if not user:
        try:
            user = await create_user(
                username=generate_username(),
                email=google_data.email,
                google_id=google_data.id,
            )
        except UserAlreadyExistsError as e:
            raise UserAlreadyExists(detail=e.message)
        except Exception as e:
            logger.error(f"Failed to create user: {e}")
            raise OAuthError(detail="Failed to create user from Google profile.")

    return Token(access_token=create_access_token(subject=user.id))  # type: ignore
