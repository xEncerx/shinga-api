from src.infrastructure.sources.source_manager import SourceManager
from src.domain.models.source import Source

from .mal import MalClient
from .remanga import RemangaClient
from .shikimori import ShikimoriClient
from .base_provider import BaseProvider
# Import other source clients as needed

AVAILABLE_SOURCES = {
    Source.SHIKIMORI: ShikimoriClient,
    Source.MAL: MalClient,
    Source.REMANGA: RemangaClient,
    # Add other sources here
}

__all__ = [
    "MalClient",
    "ShikimoriClient",
    "RemangaClient",
    "AVAILABLE_SOURCES",
    "BaseProvider",
    "SourceManager",
]
