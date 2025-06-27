from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        extra='ignore'
    )

    API_URL: str = "http://localhost:8000"

    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Shinga Api"
    VERSION: str = "0.1.0"

    COVER_STORAGE_PATH: str = "app/api/media/covers"
    COVER_PUBLIC_PATH: str = API_URL + "/api/v1/media/covers"

    OPENAI_API_KEYS: list[str] = []
    OPENAI_API_BASE: str
    OPENAI_API_MODEL: str

    # Proxy settings
    PROXY_FETCH_INTERVAL: int = 3600  # 1 hour
    PROXY_VALIDATION_INTERVAL: int = 1800  # 30 minutes
    PROXY_SOURCES: list[str] | None = None
    
    # Rate limiting
    PROXY_RPS_LIMIT: int = 3
    PROXY_RPM_LIMIT: int = 60