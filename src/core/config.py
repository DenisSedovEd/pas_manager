from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent


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

    path: str = Field(default="database.sqlite3")
    dialect: str = Field("sqlite")
    engine: str = Field("aiosqlite")
    echo: bool = Field(False)
    future: bool = Field(True)

    @property
    def url(self):
        db_path = BASE_DIR / "data" / self.path
        return f"sqlite+aiosqlite:///{db_path}"

    @property
    def sync_url(self) -> str:
        db_path = BASE_DIR / "data" / self.path
        return f"sqlite:///{db_path}"


class AppSettings(Base):
    model_config = SettingsConfigDict(
        env_prefix="APP",
    )
    host: str = Field("localhost")
    port: int = Field(8080)
    debug: bool = Field(False)
    user_id: int = Field(...)
    telegram_token: str = Field(...)
    key_length: int = Field(...)
    salt_size: int = Field(...)
    iterations: int = Field(...)
    delete_timeout_seconds: int = Field(...)


class Settings(Base):
    # noinspection PyArgumentList
    db: DbSettings = Field(default_factory=DbSettings)
    # noinspection PyArgumentList
    app: AppSettings = Field(default_factory=AppSettings)


# noinspection PyArgumentList
settings = Settings()
