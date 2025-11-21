from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent


class Base(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="",
        env_file=(BASE_DIR / ".env", BASE_DIR / ".env.template"),
        env_nested_delimiter="__",
        extra="ignore",
    )


class DbSettings(Base):
    model_config = SettingsConfigDict(
        env_prefix="DB",
    )

    user: str = Field(...)
    password: str = Field(...)
    db: str = Field(...)
    host: str = Field(...)
    port: int = Field(5432, ge=1, le=65535)
    dialect: str = Field(...)
    engine: str = Field(...)
    echo: bool = Field(False)
    future: bool = Field(True)

    @property
    def url(self):
        return f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.db}"

    @property
    def sync_url(self) -> str:
        return f"postgresql+psycopg2://{self.user}:{self.password}@{self.host}:{self.port}/{self.db}"


class AppSettings(Base):
    model_config = SettingsConfigDict(
        env_prefix="APP",
    )
    debug: bool = Field(False)
    user_id: str = Field(...)
    telegram_token: str = Field(...)


class Settings(Base):
    # noinspection PyArgumentList
    db: DbSettings = DbSettings()
    # noinspection PyArgumentList
    app: AppSettings = AppSettings()


# noinspection PyArgumentList
settings = Settings()
