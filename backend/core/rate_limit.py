import time
from collections import defaultdict

from fastapi import HTTPException, Request

_attempts: dict[str, list[float]] = defaultdict(list)
_WINDOW_SECONDS = 60
_MAX_ATTEMPTS = 5


def check_rate_limit(request: Request) -> None:
    """Блокирует IP после 5 неудачных попыток за 60 секунд."""
    ip = request.client.host if request.client else "unknown"
    now = time.time()
    window_start = now - _WINDOW_SECONDS
    _attempts[ip] = [t for t in _attempts[ip] if t > window_start]
    if len(_attempts[ip]) >= _MAX_ATTEMPTS:
        raise HTTPException(
            status_code=429,
            detail=f"Too many attempts. Try again in {_WINDOW_SECONDS} seconds.",
        )
    _attempts[ip].append(now)


def reset_rate_limit(request: Request) -> None:
    """Сбрасывает счётчик для IP после успешного входа."""
    ip = request.client.host if request.client else "unknown"
    _attempts.pop(ip, None)
