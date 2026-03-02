from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import CallbackContext, ContextTypes, ConversationHandler

from core.config import settings
from services.message_service import safe_delete, schedule_deletion
from tg_bot.keyboards import get_main_menu
from tg_bot.messages import BotMessages


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
    async def clear_all(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        context.user_data.clear()
        message_id = update.effective_message.message_id
        for i in range(50):
            try:
                await context.bot.delete_message(
                    chat_id=update.effective_chat.id,
                    message_id=message_id - i,
                )
            except Exception:
                continue

        sent_message = await update.effective_message.send_message(
            "🧹 Все действия отменены, состояние сброшено.",
            reply_markup=get_main_menu(),
        )
        await schedule_deletion(sent_message, context, delay=5)
        return ConversationHandler.END

    @staticmethod
    async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            BotMessages.CANCELLED,
            reply_markup=get_main_menu(),
        )
        return ConversationHandler.END
