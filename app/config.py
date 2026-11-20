from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    dry_run: bool = True

    devto_api_key: str = ""

    mastodon_base_url: str = "https://mastodon.social"
    mastodon_access_token: str = ""

    bluesky_handle: str = ""
    bluesky_app_password: str = ""

    telegram_bot_token: str = ""
    telegram_chat_id: str = ""

    discord_webhook_url: str = ""


@lru_cache
def get_settings() -> Settings:
    return Settings()
