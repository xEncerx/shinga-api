from pydantic import BaseModel, Field

class OAuthProfile(BaseModel):
    """Base model for OAuth profiles."""
    id: str
    email: str | None
    login: str | None