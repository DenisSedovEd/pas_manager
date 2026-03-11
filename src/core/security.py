import urllib.parse
import hmac
import hashlib
import json

from argon2 import PasswordHasher
from fastapi import HTTPException
from src.core.config import settings
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


class PasswordHelper:
    def __init__(self):
        self.pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

    def hash_password(self, password: str) -> str:
        return self.pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return self.pwd_context.verify(plain_password, hashed_password)
