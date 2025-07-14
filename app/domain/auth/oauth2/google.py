from httpx_oauth.oauth2 import OAuth2, OAuth2ClientAuthMethod
from httpx_oauth.exceptions import GetProfileError

from app.domain.models import OAuthProfile


class GoogleOAuth2(OAuth2):
    BASE_SCOPES = ["openid", "email", "profile"]

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        authorize_endpoint: str = "https://accounts.google.com/o/oauth2/v2/auth",
        access_token_endpoint: str = "https://oauth2.googleapis.com/token",
        user_info_endpoint: str = "https://www.googleapis.com/oauth2/v3/userinfo",
        refresh_token_endpoint: str | None = None,
        revoke_token_endpoint: str | None = None,
        *,
        name: str = "oauth2",
        base_scopes: list[str] = BASE_SCOPES,
        token_endpoint_auth_method: OAuth2ClientAuthMethod = "client_secret_post",
        revocation_endpoint_auth_method=None,
    ):
        self.user_info_endpoint = user_info_endpoint
        super().__init__(
            client_id,
            client_secret,
            authorize_endpoint,
            access_token_endpoint,
            refresh_token_endpoint,
            revoke_token_endpoint,
            name=name,
            base_scopes=base_scopes,
            token_endpoint_auth_method=token_endpoint_auth_method,
            revocation_endpoint_auth_method=revocation_endpoint_auth_method,
        )

    async def get_profile(self, token: str) -> OAuthProfile: # type: ignore[override]     
        """
        Gets the user profile info from Google OAuth2 service.

        Args:
            token (str): The OAuth2 access token.

        Returns:
            OAuthProfile: An instance of OAuthProfile containing some of user information.
        """   
        headers = {"Authorization": f"Bearer {token}"}

        try:
            async with self.get_httpx_client() as client:
                response = await client.get(
                    self.user_info_endpoint,
                    headers=headers,
                )
                response.raise_for_status()
                data = response.json()

                return OAuthProfile(
                    id=data["sub"],
                    email=data.get("email"),
                    login=data.get("name"),
                )
        except Exception as e:
            raise GetProfileError(message=f"Failed to get user profile: {e}")

        