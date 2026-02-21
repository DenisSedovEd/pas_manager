import logging

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
)

from src.old_bot import messages
from src.old_bot.keyboards import START_MARKUP
from src.core.config import settings

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


class BaseHandler:

    async def start_command(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
    ) -> None:
        if not await self.check_admin(update):
            return
        context.user_data.clear()
        context.user_data["messages_for_del"] = []
        await update.message.reply_text(
            messages.start_message,
            reply_markup=START_MARKUP,
            parse_mode=ParseMode.MARKDOWN,
        )

    async def check_admin(
        self,
        update: Update,
    ) -> bool:
        if update.effective_user.id != settings.app.user_id:
            if update.message:
                await update.message.reply_text(
                    "Доступ закрыт. Вы не являетесь владельцем."
                )
            return False
        return True

    async def cancel_command(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
    ) -> int:
        await update.message.reply_text(
            "Действие отменено",
        )
        return ConversationHandler.END
