"""Заголовки безопасности для ответов приложения.

Политика различается по областям, и это принципиально:

* ``/pas-manager/*`` — API. Отдаёт расшифрованные пароли и файлы иконок,
  поэтому: запрет кэширования, ``default-src 'none'`` и ``sandbox``. Последнее
  обезвреживает загруженный SVG — открытый как документ, он больше не может
  исполнить скрипт в origin приложения и сходить по API с живой сессией.
  На отображение иконок через ``<img>`` это не влияет: CSP ответа ограничивает
  только документ, а не подгрузку картинки сторонней страницей.
* ``/tg*`` — Telegram mini app. Фрейминг НЕ запрещаем: mini app открывается в
  iframe на web.telegram.org, и X-Frame-Options его просто сломает.
* ``/web*`` и ``/`` — веб-SPA. Фрейминг запрещаем полностью.

HSTS по умолчанию выключен и уходит только на https-ответах: на хосте, к
которому ходят по http из локальной сети, этот заголовок закрыл бы доступ.
"""

from starlette.types import ASGIApp

from backend.core.config import settings

API_PREFIX = "/pas-manager"
TG_PREFIX = "/tg"
WEB_PREFIX = "/web"

_COMMON = {
    "X-Content-Type-Options": "nosniff",
    "Referrer-Policy": "no-referrer",
}

# Без 'unsafe-inline' в style-src не обойтись: inline <style> в index.html и
# стили, которые Vue и emoji-picker вставляют в рантайме.
# jsdelivr разрешён только для картинок: emoji-picker вызван с native=true и
# на CDN не ходит, но пусть правка не сможет ничего сломать.
_FRONTEND_CSP_PARTS = [
    "default-src 'self'",
    "style-src 'self' 'unsafe-inline'",
    "img-src 'self' data: blob: https://cdn.jsdelivr.net",
    "font-src 'self' data:",
    "connect-src 'self'",
    "object-src 'none'",
    "base-uri 'none'",
    "form-action 'self'",
]

WEB_CSP = "; ".join(
    [*_FRONTEND_CSP_PARTS, "script-src 'self'", "frame-ancestors 'none'"]
)

# Скрипт telegram-web-app.js грузится с telegram.org — без него mini app не
# получит initData. frame-ancestors намеренно отсутствует.
TG_CSP = "; ".join([*_FRONTEND_CSP_PARTS, "script-src 'self' https://telegram.org"])

API_CSP = "default-src 'none'; frame-ancestors 'none'; base-uri 'none'; sandbox"


def _is_api(path: str) -> bool:
    return path == API_PREFIX or path.startswith(API_PREFIX + "/")


def _is_tg(path: str) -> bool:
    return path == TG_PREFIX or path.startswith(TG_PREFIX + "/")


def _is_web(path: str) -> bool:
    return path == "/" or path == WEB_PREFIX or path.startswith(WEB_PREFIX + "/")


def security_headers_for(path: str, content_type: str, scheme: str) -> dict[str, str]:
    """Набор заголовков для одного ответа.

    Вынесено из middleware отдельной функцией, чтобы политику можно было
    проверять без поднятия приложения.
    """
    headers = dict(_COMMON)

    if _is_api(path):
        headers["Content-Security-Policy"] = API_CSP
        headers["X-Frame-Options"] = "DENY"
        if content_type.startswith("image/"):
            # Иконки кэшировались и раньше (эвристикой браузера) — оставляем
            # кэш, чтобы не плодить запросы на каждую отрисовку списка.
            headers["Cache-Control"] = "private, max-age=3600"
        else:
            headers["Cache-Control"] = "no-store"
    elif _is_tg(path):
        headers["Content-Security-Policy"] = TG_CSP
    elif _is_web(path):
        headers["Content-Security-Policy"] = WEB_CSP
        headers["X-Frame-Options"] = "DENY"
    # Остальное (/docs, /openapi.json) получает только _COMMON: Swagger UI
    # тянет ресурсы с CDN, и строгий CSP сломал бы его.

    hsts = settings.app.hsts_seconds
    if hsts > 0 and scheme == "https":
        headers["Strict-Transport-Security"] = f"max-age={hsts}"

    return headers


def cookie_secure_for(scheme: str) -> bool:
    """Нужен ли флаг Secure у cookie сессии для этого запроса.

    По умолчанию — по схеме: через туннель (https) cookie помечается Secure и
    больше не может утечь по http, а доступ из локальной сети по http
    продолжает работать как раньше. Настройкой можно задать жёстко.
    """
    configured = settings.app.cookie_secure
    if configured is not None:
        return configured
    return scheme == "https"


def add_security_headers(app: ASGIApp) -> None:
    """Вешает middleware, дополняющий ответы заголовками безопасности."""

    @app.middleware("http")
    async def _security_headers(request, call_next):
        response = await call_next(request)
        extra = security_headers_for(
            request.url.path,
            response.headers.get("content-type", ""),
            request.url.scheme,
        )
        for name, value in extra.items():
            response.headers[name] = value
        return response
