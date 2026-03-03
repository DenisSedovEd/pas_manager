import time


class SessionManager:
    def __init__(self):
        # {user_id: expiry_timestamp}
        self._active_sessions: dict[int, float] = {}
        self.ttl = 2

    def create_session(self, user_id: int, ttl: int = 2):
        """Создаем сессию"""
        self._active_sessions[user_id] = time.time() + ttl

    def is_active(self, user_id: int) -> bool:
        """Проверка сессии на активность и TTL"""
        last_activity = self._active_sessions.get(user_id)
        if not last_activity:
            return False

        if time.time() - last_activity > self.ttl:
            self.close_session(user_id)
            return False

        self._active_sessions[user_id] = time.time()
        return True

    def close_session(self, user_id: int):
        """Безопасное удаление сессии"""
        self._active_sessions.pop(user_id, None)


session_manager = SessionManager()
