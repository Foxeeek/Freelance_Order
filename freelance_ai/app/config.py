from __future__ import annotations

from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=False)

    TELEGRAM_BOT_TOKEN: str = ""
    TELEGRAM_CHAT_ID: str = ""
    ENABLED_PLATFORMS: list[str] = Field(default_factory=lambda: ["freelancehunt"])
    POLL_INTERVAL_MINUTES: int = 10
    HOURLY_RATE_EUR: int = 15
    DEFAULT_LANGUAGE: str = "en"
    DATABASE_URL: str = "sqlite:///./freelance_ai.db"

    @field_validator("ENABLED_PLATFORMS", mode="before")
    @classmethod
    def _parse_enabled_platforms(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, list):
            return [item.strip().lower() for item in value if item.strip()]
        if isinstance(value, str):
            return [item.strip().lower() for item in value.split(",") if item.strip()]
        return []

    @field_validator("DEFAULT_LANGUAGE")
    @classmethod
    def _validate_language(cls, value: str) -> str:
        lowered = value.lower().strip()
        return lowered if lowered in {"en", "ua"} else "en"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
