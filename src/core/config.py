from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent


class DbSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="DB",
        env_file=(BASE_DIR / ".env", BASE_DIR / ".env.template"),
        env_nested_delimiter="__",
        extra="ignore",
    )
