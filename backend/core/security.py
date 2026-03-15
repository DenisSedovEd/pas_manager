import time
import urllib.parse
import hmac
import hashlib
import json

from argon2 import PasswordHasher
from fastapi import HTTPException
from backend.core.config import settings
from passlib.context import CryptContext


def verify_telegram_data(init_data: str) -> dict:
    if not init_data:
        raise HTTPException(status_code=400, detail="Missing initData")

    parsed_data = urllib.parse.parse_qs(init_data)
    if "hash" not in parsed_data:
        raise HTTPException(status_code=400, detail="Invalid initData format")

    received_hash = parsed_data.pop("hash")[0]

    # Сортируем ключи и собираем строку для проверки
    data_check_string = "\n".join(f"{k}={v[0]}" for k, v in sorted(parsed_data.items()))

    # Вычисляем секретный ключ
    secret_key = hmac.new(
        b"WebAppData", settings.app.telegram_token.encode(), hashlib.sha256
    ).digest()
    computed_hash = hmac.new(
        secret_key, data_check_string.encode(), hashlib.sha256
    ).hexdigest()

    if computed_hash != received_hash:
        raise HTTPException(status_code=401, detail="Authentication failed")

    user_data = json.loads(parsed_data["user"][0])
    auth_date = int(parsed_data.get("auth_date", [0])[0])
    if abs(time.time() - auth_date) > settings.app.session_ttl:
        raise HTTPException(status_code=401, detail="Init data expired")
    if str(user_data.get("id", "")) != str(settings.app.user_id):
        raise HTTPException(status_code=403, detail="Access denied")
    return user_data


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
