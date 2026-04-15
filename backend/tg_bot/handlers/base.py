from telegram import Update
from telegram.ext import ContextTypes

from backend.core.config import settings
from backend.core.session import session_manager


def is_admin(update: Update) -> bool:
    """Проверяет, что сообщение от администратора."""
    return update.effective_user.id == settings.tg.user_id


def require_admin(func):
    """Декоратор — отклоняет запросы не от администратора."""

    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not is_admin(update):
            await update.effective_message.reply_text("⛔ Доступ запрещён.")
            return
        return await func(update, context)

    return wrapper


def require_session(func):
    """Декоратор — требует активную разблокированную сессию."""

    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not is_admin(update):
            await update.effective_message.reply_text("⛔ Доступ запрещён.")
            return
        if not session_manager.is_active(settings.tg.user_id):
            await update.effective_message.reply_text(
                "🔒 Сейф заблокирован. Введи /unlock чтобы разблокировать."
            )
            return
        return await func(update, context)

    return wrapper
