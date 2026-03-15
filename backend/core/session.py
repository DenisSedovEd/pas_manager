import time

from backend.core.config import settings


class SessionManager:
    def __init__(self):
        # {user_id: expiry_timestamp}
        self._active_sessions: dict[str, dict] = {}
        self.ttl = settings.app.session_ttl

    def create_session(self, user_id: int, master_password: str, ttl: int = None):
        """Создаем сессию с мастер-паролем"""
        if ttl is None:
            ttl = self.ttl

        self._active_sessions[user_id] = {
            "expiry": time.time() + ttl,
            "master_password": master_password,
        }

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

    def close_session(self, user_id: int):
        """Безопасное удаление сессии"""
        self._active_sessions.pop(user_id, None)


session_manager = SessionManager()
