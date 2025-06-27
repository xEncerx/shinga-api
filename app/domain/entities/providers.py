from pydantic import BaseModel, Field

__all__ = (
    "ProviderInfo",
    "MalProvider",
    "RemangaProvider",
    "ShikimoriProvider",
    "TitleProviders",
)

class ProviderInfo(BaseModel):
    """Information about a provider."""

    name: str = Field(..., description="Name of the provider")
    title_id: str | int | None = Field(..., description="Unique identifier for the title in the provider's system")

class MalProvider(ProviderInfo):
    """Provider information specific to MyAnimeList."""
    name: str = Field("MyAnimeList", description="Name of the MyAnimeList provider")

class RemangaProvider(ProviderInfo):
    """Provider information specific to Remanga."""
    name: str = Field("Remanga", description="Name of the Remanga provider")

class ShikimoriProvider(ProviderInfo):
    """Provider information specific to Shikimori."""
    name: str = Field("Shikimori", description="Name of the Shikimori provider")

class TitleProviders(BaseModel):
    """Providers for the title."""
    mal: MalProvider | None = Field(default=None, description="Information about the MyAnimeList provider")
    remanga: RemangaProvider | None = Field(default=None, description="Information about the Remanga provider")
    shikimori: ShikimoriProvider | None = Field(default=None, description="Information about the Shikimori provider")