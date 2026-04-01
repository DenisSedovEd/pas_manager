from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

from backend.dependencies import get_account_service
from backend.services.message_service import schedule_deletion, safe_delete
from backend.tg_bot.keyboards import get_main_menu
from backend.tg_bot.messages import BotMessages
from backend.tg_bot.states import ListAccountStates as States


class ViewAccountHandler:
    async def ask_master_password(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        query = update.callback_query
        await query.answer()
        await query.message.delete()

        sent_msg = await update.effective_chat.send_message(
            BotMessages.ENTER_MASTER_PASS
        )
        await schedule_deletion(sent_msg, context, delay=60)
        return States.WAITING_MASTER_VIEW

    async def show_decrypted_credentials(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        await safe_delete(update.message)
        master_password = update.message.text

        # ИСПРАВЛЕНО: Ищем по ключу "selected_service"
        service_name = context.user_data.get("selected_service")

        if not service_name:
            sent_msg = await update.effective_chat.send_message(
                "❌ Ошибка: сервис не выбран. Начните заново."
            )
            await schedule_deletion(sent_msg, context, delay=10)
            return ConversationHandler.END

        async with get_account_service() as service:
            try:
                account = await service.get_account(service_name, master_password)

                text = (
                    f"🔐 **Данные для {account.service_name}**\n\n"
                    f"👤 Логин: `{account.username}`\n"
                    f"🔑 Пароль: `{account.password}`"
                )

                sent_msg = await update.effective_chat.send_message(
                    text,
                    parse_mode="MarkdownV2",
                    reply_markup=get_main_menu(),
                )
                await schedule_deletion(sent_msg, context, delay=30)

            except ValueError as e:
                sent_msg = await update.effective_chat.send_message(
                    f"❌ Ошибка: {str(e)}"
                )
                await schedule_deletion(sent_msg, context, delay=10)

            return ConversationHandler.END


view_handler = ViewAccountHandler()
