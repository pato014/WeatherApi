from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str  = "Weather API"
    openweather_api_key: str = Field(..., alias="OPENWEATHER_API_KEY")
    openweather_base_url: str = "https://api.openweathermap.org/data/2.5/weather"
    units: str = Field(default="metric", alias="UNITS")

    data_dir: str = Field(default="data", alias="DATA_DIR")
    sqlite_path: str = Field(default="app.db", alias="SQLITE_PATH")

    redis_url: str = Field(default="redis://localhost:6379/0", alias="REDIS_URL")
    cache_ttl_seconds: int = Field(default=300, alias="CACHE_TTL_SECONDS")

    http_timeout_seconds: float = Field(default=10.0, alias="HTTP_TIMEOUT_SECONDS")


settings = Settings()
