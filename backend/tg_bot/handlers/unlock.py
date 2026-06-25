from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

from backend.core.config import settings
from backend.core.db import async_session
from backend.core.security import MasterPasswordService
from backend.core.session import session_manager
from backend.models import AppSettings
from backend.repositories import DatabaseRepository
from backend.tg_bot.handlers.base import is_admin

AWAITING_PASSWORD = 0


async def cmd_unlock(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if not is_admin(update):
        await update.message.reply_text("⛔ Доступ запрещён.")
        return ConversationHandler.END

    if session_manager.is_active(settings.tg.user_id):
        await update.message.reply_text(
            "✅ Сейф уже разблокирован. /categories для списка категорий."
        )
        return ConversationHandler.END

    await update.message.reply_text("🔑 Введи мастер-пароль:")
    return AWAITING_PASSWORD


async def receive_password(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    password = update.message.text.strip()

    async with async_session() as db:
        db_repo = DatabaseRepository(db)
        app_settings = await db_repo.get(
            AppSettings, filters={"id": settings.app.admin_id}
        )

    if not app_settings:
        await update.message.reply_text("❌ Настройки приложения не инициализированы.")
        return ConversationHandler.END

    if MasterPasswordService().verify_password(
        password, app_settings.master_password_hash
    ):
        session_manager.create_miniapp_session(settings.tg.user_id, password)
        await update.message.reply_text(
            "✅ Сейф разблокирован!\n\n"
            "/categories — список категорий\n"
            "/lock — заблокировать"
        )
        return ConversationHandler.END

    await update.message.reply_text(
        "❌ Неверный пароль. Попробуй ещё раз или /cancel для отмены:"
    )
    return AWAITING_PASSWORD


async def cmd_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Отменено.")
    return ConversationHandler.END
