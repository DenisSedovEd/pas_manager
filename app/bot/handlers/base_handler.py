from telegram import Update
from telegram.ext import (
    ConversationHandler,
    ContextTypes,
)

from app.core.config import settings


class BaseHandler:

    @staticmethod
    async def check_admin(update: Update) -> bool:
        if update.effective_user.id != settings.app.user_id:
            if update.message:
                await update.message.reply_text(
                    "Доступ закрыт. Вы не являетесь владельцем."
                )
            return False
        return True

    @staticmethod
    async def cancel_command(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
    ) -> int:
        await update.message.reply_text("Действие отменено")
        return ConversationHandler.END
