from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "CryptoPilot"
    api_v1_prefix: str = "/api/v1"
    database_url: str = "sqlite+aiosqlite:///./cryptopilot.db"
    redis_url: str = "redis://localhost:6379/0"
    backend_cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:5173"])
    market_universe_max: int = 20
    ingestion_history_days: int = 90
    model_config = SettingsConfigDict(env_file=".env", env_nested_delimiter="__", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
