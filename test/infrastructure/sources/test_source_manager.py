import asyncio

from src.domain.models.source import Source
from src.infrastructure.sources.base_provider import BaseProvider
from src.infrastructure.sources.source_manager import SourceManager


class _HeadersLoader:
    def load(self, source):
        return {"X-Source": source.name.lower()}


class _Provider(BaseProvider):
    async def create_session(self):
        return None

    async def get_by_id(self, external_id):
        return None

    async def get_page(self, page=1, limit=25):
        return []

    async def get_source_detail(self):
        raise NotImplementedError


class TestSourceManager:
    def test_initialize_passes_source_headers_to_provider(self):
        manager = SourceManager(
            providers={Source.REMANGA: _Provider},
            headers_loader=_HeadersLoader(),  # type: ignore
        )

        asyncio.run(manager.initialize())

        provider = manager.get_provider(Source.REMANGA)
        assert provider._base_headers == {"X-Source": "remanga"}
