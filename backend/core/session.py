import time
import uuid
from typing import Literal

from backend.core.config import settings

SessionKind = Literal["web", "miniapp"]
KIND_WEB: SessionKind = "web"
KIND_MINIAPP: SessionKind = "miniapp"


class SessionManager:
    def __init__(self):
        self._active_sessions: dict[tuple[int, SessionKind], dict] = {}
        self._tokens: dict[str, tuple[int, SessionKind]] = {}
        self.ttl_web = settings.app.session_ttl_web
        self.ttl_miniapp = settings.app.session_ttl_miniapp

    def _key(self, user_id: int, kind: SessionKind) -> tuple[int, SessionKind]:
        return user_id, kind

    def create_session(
        self,
        user_id: int,
        master_password: str,
        kind: SessionKind,
        ttl: int | None = None,
    ) -> None:
        """Создаем сессию с мастер-паролем для конкретного клиента."""
        session_ttl = ttl if ttl is not None else (
            self.ttl_web if kind == KIND_WEB else self.ttl_miniapp
        )

        self._active_sessions[self._key(user_id, kind)] = {
            "expiry": time.time() + session_ttl,
            "master_password": master_password,
            "ttl": session_ttl,
        }

    def create_browser_session(self, user_id: int, master_password: str) -> str:
        """Создаем веб-сессию и возвращаем UUID-токен для cookie."""
        self.create_session(user_id, master_password, KIND_WEB, ttl=self.ttl_web)
        token = str(uuid.uuid4())
        self._tokens[token] = self._key(user_id, KIND_WEB)
        return token

    def create_miniapp_session(self, user_id: int, master_password: str) -> None:
        """Создаем сессию для Telegram mini app и бота."""
        self.create_session(user_id, master_password, KIND_MINIAPP, ttl=self.ttl_miniapp)

    def verify_browser_token(self, token: str) -> int | None:
        """Возвращаем user_id по веб-токену или None."""
        session_key = self._tokens.get(token)
        if session_key is None:
            return None
        user_id, kind = session_key
        if kind != KIND_WEB:
            return None
        if not self.is_active(user_id, kind):
            self._tokens.pop(token, None)
            return None
        return user_id

    def is_active(self, user_id: int, kind: SessionKind) -> bool:
        """Проверка сессии клиента на активность и TTL."""
        session = self._active_sessions.get(self._key(user_id, kind))
        if not session:
            return False

        if time.time() > session["expiry"]:
            self.close_session(user_id, kind)
            return False

        session["expiry"] = time.time() + session["ttl"]
        return True

    def get_master_password(self, user_id: int, kind: SessionKind) -> str | None:
        """Получить мастер-пароль из сессии клиента."""
        if not self.is_active(user_id, kind):
            return None
        session = self._active_sessions.get(self._key(user_id, kind))
        return session["master_password"] if session else None

    def close_session(self, user_id: int, kind: SessionKind) -> None:
        """Удалить сессию конкретного клиента и связанные веб-токены."""
        self._active_sessions.pop(self._key(user_id, kind), None)
        if kind == KIND_WEB:
            stale = [t for t, key in self._tokens.items() if key == self._key(user_id, KIND_WEB)]
            for token in stale:
                self._tokens.pop(token, None)


session_manager = SessionManager()
