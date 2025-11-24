import logging

from telegram import Update, ReplyKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import (
    ConversationHandler,
    ContextTypes,
)

from app.core.config import settings
from app.bot.keyboards import MAIN_MENU_MARKUP
from app.bot import messages

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


class BaseHandler:

    # def __init__(self):
    #     self.main_menu_markup = MAIN_MENU_MARKUP

    async def start_command(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
    ) -> None:
        if not await self.check_admin(update):
            return
        await update.message.reply_text(
            messages.start_message,
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

    async def delete_secure_message(self, context: ContextTypes.DEFAULT_TYPE):
        chat_id, message_id = context.job.data

        try:
            await context.bot.delete_message(
                chat_id=chat_id,
                message_id=message_id,
            )
            logger.info("Сообщение с кредами удалено.")
        except Exception as e:
            logger.error(e)
