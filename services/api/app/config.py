from __future__ import annotations

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "GeoAdmin API"
    app_env: str = "development"
    app_version: str = "0.1.0"
    debug: bool = True
    supabase_url: str | None = Field(
        default=None,
        validation_alias=AliasChoices("GEOADMIN_SUPABASE_URL", "SUPABASE_URL"),
    )
    supabase_key: str | None = Field(
        default=None,
        validation_alias=AliasChoices("GEOADMIN_SUPABASE_KEY", "SUPABASE_KEY"),
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="GEOADMIN_",
        extra="ignore",
    )


settings = Settings()
