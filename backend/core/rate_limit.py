import time

from fastapi import HTTPException, Request

from backend.core.config import settings as app_settings

# Ключ — (scope, ip): у веб-входа, входа в mini app и биометрии отдельные
# бюджеты, иначе неудачи в одном клиенте съедают попытки другого. За прокси
# все запросы приходят с одного IP, поэтому разделение по scope важно.
_attempts: dict[tuple[str, str], list[float]] = {}

# Чтобы словарь не рос без предела от перебора с разных адресов.
_MAX_TRACKED_KEYS = 10_000


def _client_ip(request: Request) -> str:
    return request.client.host if request.client else "unknown"


def _prune(now: float, window_seconds: int) -> None:
    """Выбрасывает ключи, у которых не осталось попыток в окне."""
    window_start = now - window_seconds
    stale = [
        key for key, hits in _attempts.items() if not hits or hits[-1] <= window_start
    ]
    for key in stale:
        _attempts.pop(key, None)


def check_rate_limit(request: Request, scope: str = "default") -> None:
    """Блокирует IP после настроенного числа попыток за окно времени."""
    window_seconds = app_settings.app.rate_limit_window_seconds
    max_attempts = app_settings.app.rate_limit_max_attempts
    now = time.time()
    window_start = now - window_seconds
    key = (scope, _client_ip(request))

    _prune(now, window_seconds)

    hits = [t for t in _attempts.get(key, []) if t > window_start]
    if len(hits) >= max_attempts:
        _attempts[key] = hits
        raise HTTPException(
            status_code=429,
            detail=f"Too many attempts. Try again in {window_seconds} seconds.",
        )

    # Переполнение возможно только при распределённом переборе: отказываем
    # в обслуживании новым ключам, но уже отслеживаемые продолжаем считать.
    if key not in _attempts and len(_attempts) >= _MAX_TRACKED_KEYS:
        raise HTTPException(
            status_code=429,
            detail=f"Too many attempts. Try again in {window_seconds} seconds.",
        )

    hits.append(now)
    _attempts[key] = hits


def reset_rate_limit(request: Request, scope: str = "default") -> None:
    """Сбрасывает счётчик для IP после успешного входа."""
    _attempts.pop((scope, _client_ip(request)), None)
