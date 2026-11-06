import time
from collections import defaultdict

from fastapi import HTTPException, Request

from backend.core.config import settings as app_settings

_attempts: dict[str, list[float]] = defaultdict(list)


def check_rate_limit(request: Request) -> None:
    """Блокирует IP после настроенного числа неудачных попыток за окно времени."""
    window_seconds = app_settings.app.rate_limit_window_seconds
    max_attempts = app_settings.app.rate_limit_max_attempts
    ip = request.client.host if request.client else "unknown"
    now = time.time()
    window_start = now - window_seconds
    _attempts[ip] = [t for t in _attempts[ip] if t > window_start]
    if len(_attempts[ip]) >= max_attempts:
        raise HTTPException(
            status_code=429,
            detail=f"Too many attempts. Try again in {window_seconds} seconds.",
        )
    _attempts[ip].append(now)


def reset_rate_limit(request: Request) -> None:
    """Сбрасывает счётчик для IP после успешного входа."""
    ip = request.client.host if request.client else "unknown"
    _attempts.pop(ip, None)
