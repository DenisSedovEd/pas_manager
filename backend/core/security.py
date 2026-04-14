import hashlib
import hmac
import json
import urllib.parse

from argon2 import PasswordHasher
from fastapi import HTTPException

from backend.core.config import settings
from backend.core.session import session_manager


def verify_telegram_data(init_data: str) -> dict:
    if not init_data:
        raise HTTPException(status_code=400, detail="Missing initData")

    parsed_data = urllib.parse.parse_qs(init_data)
    if "hash" not in parsed_data:
        raise HTTPException(status_code=400, detail="Invalid initData format")

    received_hash = parsed_data.pop("hash")[0]

    data_check_string = "\n".join(f"{k}={v[0]}" for k, v in sorted(parsed_data.items()))

    secret_key = hmac.new(
        b"WebAppData", settings.tg.telegram_token.encode(), hashlib.sha256
    ).digest()
    computed_hash = hmac.new(
        secret_key, data_check_string.encode(), hashlib.sha256
    ).hexdigest()

    if computed_hash != received_hash:
        raise HTTPException(status_code=401, detail="Authentication failed")

    user_data = json.loads(parsed_data["user"][0])
    if str(user_data.get("id", "")) != str(settings.tg.user_id):
        raise HTTPException(status_code=403, detail="Access denied")
    return user_data


def verify_browser_token(token: str) -> dict:
    """Проверяет UUID-токен браузерной сессии, возвращает {"id": user_id}."""
    user_id = session_manager.verify_browser_token(token)
    if user_id is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return {"id": user_id}


class MasterPasswordService:
    def __init__(self):
        self.ph = PasswordHasher()

    def hash_password(self, password: str) -> str:
        """Создает безопасный хэш для хранения в БД."""
        return self.ph.hash(password)

    def verify_password(self, password: str, hashed: str) -> bool:
        """Проверяет введенный пароль на соответствие хэшу."""
        try:
            return self.ph.verify(hashed, password)
        except Exception:
            return False
