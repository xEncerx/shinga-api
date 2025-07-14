from httpx_oauth.oauth2 import OAuth2, OAuth2ClientAuthMethod
from httpx_oauth.exceptions import GetProfileError

from app.domain.models import OAuthProfile


class YandexOAuth2(OAuth2):
    BASE_SCOPES = ["login:email", "login:info"]

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        authorize_endpoint: str = "https://oauth.yandex.ru/authorize",
        access_token_endpoint: str = "https://oauth.yandex.ru/token",
        user_info_endpoint: str = "https://login.yandex.ru/info",
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
        Gets the user profile info from Yandex OAuth2 service.

        Args:
            token (str): The OAuth2 access token.

        Returns:
            OAuthProfile: An instance of OAuthProfile containing some of user information.
        """   
        headers = {"Authorization": f"OAuth {token}"}

        try:
            async with self.get_httpx_client() as client:
                response = await client.get(
                    self.user_info_endpoint,
                    headers=headers,
                )
                response.raise_for_status()
                data = response.json()

                return OAuthProfile(
                    id=data["id"],
                    email=data.get("default_email"),
                    login=data.get("login"),
                )
        except Exception as e:
            raise GetProfileError(message=f"Failed to get user profile: {e}")

        