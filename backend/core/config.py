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
    rate_limit_max_attempts: int = Field(5)
    rate_limit_window_seconds: int = Field(60)
    cookie_secure: bool | None = Field(
        default=None,
        description=(
            "Флаг Secure у cookie сессии. None — определять по схеме запроса: "
            "https получает Secure, локальный http остаётся рабочим. "
            "True/False — принудительно."
        ),
    )
    hsts_seconds: int = Field(
        default=0,
        description=(
            "max-age для Strict-Transport-Security; 0 — не отправлять. "
            "Заголовок уходит только на https-ответах, но включать его стоит "
            "осознанно: он запрещает браузеру ходить на этот хост по http."
        ),
    )
    forwarded_allow_ips: str | None = Field(
        default=None,
        description=(
            "Каким узлам доверять X-Forwarded-For/-Proto. None — значение по "
            "умолчанию uvicorn (127.0.0.1). Нужно задать, если приложение "
            "стоит за cloudflared/реверс-прокси, иначе rate limit видит один "
            "IP прокси на всех, а схема запроса определяется как http."
        ),
    )
    expose_docs: bool | None = Field(
        default=None,
        description="Отдавать /docs и /openapi.json. None — следовать debug.",
    )
    init_data_max_age_seconds: int = Field(
        default=86400,
        description=(
            "Максимальный возраст auth_date в initData Telegram; 0 — не "
            "проверять. Без проверки перехваченная строка initData остаётся "
            "действительным пропуском бессрочно."
        ),
    )
    session_absolute_ttl_web: int = Field(
        default=0,
        description=(
            "Жёсткий предел жизни веб-сессии от момента входа, секунды; "
            "0 — без предела (TTL продлевается на каждом запросе)."
        ),
    )
    session_absolute_ttl_miniapp: int = Field(
        default=0,
        description="То же для сессии mini app; 0 — без предела.",
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
