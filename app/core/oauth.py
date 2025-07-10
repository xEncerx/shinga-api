from httpx_oauth.integrations.fastapi import OAuth2AuthorizeCallback

from app.domain.auth.oauth2 import YandexOAuth2
from fastapi import Depends

from app.core import settings

yandex_oauth = YandexOAuth2(
    name="yandex",
    client_id=settings.YANDEX_CLIENT_ID,
    client_secret=settings.YANDEX_CLIENT_SECRET,
)
YandexCallbackDep = Depends(
    OAuth2AuthorizeCallback(
        yandex_oauth,
        redirect_url=settings.YANDEX_REDIRECT_URI,
    )
)
