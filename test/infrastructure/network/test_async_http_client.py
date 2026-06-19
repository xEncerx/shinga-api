from src.infrastructure.network import AsyncHttpClient


class _FakeRequestContext:
    async def __aenter__(self):
        return object()


class _FakeSession:
    closed = False

    def __init__(self):
        self.headers = None

    def request(self, method, url, **kwargs):
        self.headers = kwargs["headers"]
        return _FakeRequestContext()


class TestAsyncHttpClient:
    def test_request_merges_base_headers_with_request_headers(self):
        client = AsyncHttpClient(
            base_headers={
                "Authorization": "Bearer base-token",
                "X-Source": "remanga",
            }
        )
        fake_session = _FakeSession()
        client._session = fake_session  # type: ignore

        request = client.get(
            "titles", headers={"Authorization": "Bearer request-token"}
        )

        assert fake_session.headers["Authorization"] == "Bearer request-token"
        assert fake_session.headers["X-Source"] == "remanga"
        assert "User-Agent" in fake_session.headers  # type: ignore
        request._coro.close()
