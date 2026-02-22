from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import CallbackContext, ContextTypes, ConversationHandler

from src.core.config import settings
from src.services.message_service import safe_delete, schedule_deletion
from src.tg_bot.keyboards import get_main_menu
from src.tg_bot.messages import BotMessages


class BaseHandler:
    @staticmethod
    async def check_admin(update: Update) -> bool:
        user_id = update.effective_user.id
        if user_id != settings.app.user_id:
            await update.effective_message.reply_text(BotMessages.ACCESS_DENIED)
            return False
        return True

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await safe_delete(update.message)
        if not await self.check_admin(update):
            return
        sent_message = await update.message.reply_text(
            BotMessages.WELCOME, reply_markup=get_main_menu()
        )
        await schedule_deletion(sent_message, context, delay=1200)

    @staticmethod
    async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.delete()
        sent_msg = await update.message.reply_text(
            BotMessages.CANCELLED,
            reply_markup=get_main_menu(),
        )
        await safe_delete(sent_msg)
        return ConversationHandler.END
