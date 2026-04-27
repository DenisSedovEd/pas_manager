import time
import uuid

from backend.core.config import settings


class SessionManager:
    def __init__(self):
        self._active_sessions: dict[int, dict] = {}
        self._tokens: dict[str, int] = {}
        self.ttl = settings.app.session_ttl

    def create_session(
        self, user_id: int, master_password: str, ttl: int | None = None
    ) -> None:
        """Создаем сессию с мастер-паролем"""
        if ttl is None:
            ttl = self.ttl

        self._active_sessions[user_id] = {
            "expiry": time.time() + ttl,
            "master_password": master_password,
        }

    def create_browser_session(self, user_id: int, master_password: str) -> str:
        """Создаем сессию для браузерного клиента, возвращаем UUID-токен"""
        self.create_session(user_id, master_password)
        token = str(uuid.uuid4())
        self._tokens[token] = user_id
        return token

    def verify_browser_token(self, token: str) -> int | None:
        """Возвращаем user_id по токену, либо None если токен невалиден/сессия истекла"""
        user_id = self._tokens.get(token)
        if user_id is None:
            return None
        if not self.is_active(user_id):
            self._tokens.pop(token, None)
            return None
        return user_id

    def is_active(self, user_id: int) -> bool:
        """Проверка сессии на активность и TTL"""
        session = self._active_sessions.get(user_id)
        if not session:
            return False

        if time.time() > session["expiry"]:
            self.close_session(user_id)
            return False

        # Обновляем время жизни при каждом обращении
        session["expiry"] = time.time() + self.ttl
        return True

    def get_master_password(self, user_id: int) -> str | None:
        """Получить мастер-пароль из сессии"""
        session = self._active_sessions.get(user_id)
        if session and self.is_active(user_id):
            return session["master_password"]
        return None

    def close_session(self, user_id: int) -> None:
        """Безопасное удаление сессии и связанных токенов"""
        self._active_sessions.pop(user_id, None)
        stale = [t for t, uid in self._tokens.items() if uid == user_id]
        for t in stale:
            self._tokens.pop(t, None)


session_manager = SessionManager()
