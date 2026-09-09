from pathlib import Path
from urllib.parse import quote_plus

from pydantic import Field, model_validator
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

    host: str = Field(...)
    port: int = Field(5432)
    name: str = Field(...)
    user: str = Field(...)
    password: str = Field(...)
    echo: bool = Field(False)
    future: bool = Field(True)
    sqlite_path: str = Field(
        default="accounts.sqlite",
        description="Путь к файлу SQLite относительно data/ для одноразового переноса",
    )

    @property
    def url(self) -> str:
        """Async URL для приложения (asyncpg)."""
        return (
            f"postgresql+asyncpg://{quote_plus(self.user)}:{quote_plus(self.password)}"
            f"@{self.host}:{self.port}/{self.name}"
        )

    @property
    def sync_url(self) -> str:
        """Sync URL для Alembic (psycopg)."""
        return (
            f"postgresql+psycopg://{quote_plus(self.user)}:{quote_plus(self.password)}"
            f"@{self.host}:{self.port}/{self.name}"
        )


class AppSettings(Base):
    model_config = SettingsConfigDict(
        env_prefix="APP",
    )
    host: str = Field("localhost")
    port: int = Field(8080)
    debug: bool = Field(False)
    delete_timeout_seconds: int = Field(...)
    session_ttl: int | None = Field(
        default=None,
        description="Устаревший общий TTL; используется, если не заданы отдельные значения",
    )
    session_ttl_web: int | None = Field(default=None)
    session_ttl_miniapp: int | None = Field(default=None)
    tunnel_token: str = Field(...)
    admin_id: int = Field(...)
    cors_origins: list[str] = Field(
        default=["https://web.telegram.org", "https://t.me"]
    )

    @model_validator(mode="after")
    def resolve_session_ttl(self):
        fallback = self.session_ttl if self.session_ttl is not None else 3600
        if self.session_ttl_web is None:
            self.session_ttl_web = fallback
        if self.session_ttl_miniapp is None:
            self.session_ttl_miniapp = fallback
        return self


class TgSettings(Base):
    model_config = SettingsConfigDict(
        env_prefix="TG",
    )
    user_id: int = Field(...)
    telegram_token: str = Field(...)


class CryptoSettings(Base):
    model_config = SettingsConfigDict(
        env_prefix="CRYPTO",
    )
    key_length: int = Field(...)
    salt_size: int = Field(...)
    iterations: int = Field(...)


class Settings(Base):
    # noinspection PyArgumentList
    db: DbSettings = Field(default_factory=DbSettings)
    # noinspection PyArgumentList
    app: AppSettings = Field(default_factory=AppSettings)
    # noinspection PyArgumentList
    tg: TgSettings = Field(default_factory=TgSettings)
    # noinspection PyArgumentList
    crypto: CryptoSettings = Field(default_factory=CryptoSettings)


# noinspection PyArgumentList
settings = Settings()
