from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from app.bot import messages
from app.bot.handlers.base_handler import BaseHandler
from app.repositories import AccountRepository
from app.services.message_service import schedule_message_deletion


class ListAccountsHandler(BaseHandler):
    async def get_list_accounts(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
    ):
        welcome_message = await update.message.reply_text(
            messages.start_list_accounts,
            parse_mode=ParseMode.HTML,
        )

        await schedule_message_deletion(
            welcome_message,
            context=context,
            delay_seconds=30,
        )

        all_massage = []

        async with AccountRepository as repo:
            response = await repo.get_accounts()

        for account in response:
            keyboard = [
                [
                    InlineKeyboardButton(
                        "🔑 Получить", callback_data=f"get:{account.service_name}"
                    ),
                    InlineKeyboardButton(
                        "✏️ Редактировать",
                        callback_data=f"edit:{account.service_name}",
                    ),
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            msg = await update.message.reply_text(
                f"Сервис: {account.service_name}",
                reply_markup=reply_markup,
                parse_mode=ParseMode.HTML,
            )

            all_massage.append(msg)

        context.user_data["list_accounts"] = all_massage

    async def handle_callback_query(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        query = update.callback_query
        await query.answer()

        data = query.data.split(":")
        action = data[0]

        if action == "get":
            await query.answer()
        elif action == "edit":
            pass
        else:
            raise Exception(f"Unknown action: {action}")


list_handler_instance = ListAccountsHandler()
