from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
    CallbackQueryHandler,
    CallbackContext,
    CommandHandler,
)

from backend.dependencies import get_account_service
from backend.services.message_service import safe_delete, schedule_deletion
from backend.tg_bot.handlers.base import BaseHandler
from backend.tg_bot.handlers.edit_account import edit_handler
from backend.tg_bot.handlers.view_account import view_handler
from backend.tg_bot.keyboards import get_main_menu
from backend.tg_bot.messages import BotMessages
from backend.tg_bot.states import ListAccountStates as States
from backend.tg_bot.handlers.add_account import logic as add_logic
from backend.utils.password_generator import escape_md


class ListAccountsHandler:
    async def show_accounts_list(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        query = update.callback_query

        if query:
            await query.answer()
            try:
                await query.message.delete()
            except Exception:
                pass
        else:
            await safe_delete(update.message)

        async with get_account_service() as service:
            accounts = await service.get_accounts()

        if not accounts:
            sent_msg = await update.effective_chat.send_message(
                "📭 Список аккаунтов пока пуст."
            )
            await schedule_deletion(sent_msg, context, delay=10)
            return ConversationHandler.END

        keyboard = [
            [
                InlineKeyboardButton(
                    acc.service_name, callback_data=f"select_{acc.service_name}"
                )
            ]
            for acc in accounts
        ]

        sent_msg = await update.effective_chat.send_message(
            text=BotMessages.LIST_INTRO, reply_markup=InlineKeyboardMarkup(keyboard)
        )

        await schedule_deletion(sent_msg, context, delay=60)
        return States.SELECTING_ACCOUNT

    async def account_choice_handler(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        query = update.callback_query
        await query.answer()

        _service_name = query.data.replace("select_", "")
        service_name = escape_md(_service_name)

        context.user_data["selected_service"] = service_name

        keyboard = [
            [InlineKeyboardButton(BotMessages.BTN_GET, callback_data="action_view")],
            [InlineKeyboardButton(BotMessages.BTN_EDIT, callback_data="action_edit")],
            [
                InlineKeyboardButton(
                    BotMessages.BTN_DELETE, callback_data="action_delete"
                )
            ],
            [InlineKeyboardButton(BotMessages.BTN_BACK, callback_data="back_to_list")],
        ]

        await query.edit_message_text(
            text=BotMessages.ACCOUNT_MENU.format(service=service_name),
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown",
        )
        return States.SELECTING_ACTION

    async def ask_delete_confirmation(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        query = update.callback_query
        await query.answer()
        await query.message.delete()

        service_name = context.user_data.get("selected_service")

        sent_msg = await update.effective_chat.send_message(
            f"⚠️ **УДАЛЕНИЕ АККАУНТА: {service_name}**\n\n"
            "Для подтверждения удаления, пожалуйста, введите ваш **Мастер-пароль**.\n"
            "Или нажмите «Отмена» на клавиатуре ниже.",
            parse_mode="Markdown",
            reply_markup=get_main_menu(),
        )
        await schedule_deletion(sent_msg, context, delay=60)
        return States.CONFIRM_DELETE

    async def execute_deletion(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        await safe_delete(update.message)
        master_password = update.message.text
        service_name = context.user_data.get("selected_service")
        async with get_account_service() as service:
            try:
                await service.delete_account(service_name, master_password)
                sent_msg = await update.effective_chat.send_message(
                    f"✅ Аккаунт **{service_name}** успешно удален.",
                    parse_mode="Markdown",
                    reply_markup=get_main_menu(),
                )
                await schedule_deletion(sent_msg, context, delay=10)
            except Exception as e:
                sent_msg = await update.effective_chat.send_message(
                    f"❌ Ошибка удаления: {str(e)}", reply_markup=get_main_menu()
                )
                await schedule_deletion(sent_msg, context, delay=15)
                return await self.account_choice_handler(update, context)

            return await self.show_accounts_list(update, context)


logic = ListAccountsHandler()
base = BaseHandler()

list_accounts_conv = ConversationHandler(
    entry_points=[
        MessageHandler(filters.Text([BotMessages.BTN_LIST]), logic.show_accounts_list),
        CommandHandler("list", logic.show_accounts_list),
        CommandHandler("view", logic.show_accounts_list),
    ],
    states={
        States.SELECTING_ACCOUNT: [
            CallbackQueryHandler(logic.account_choice_handler, pattern="^select_"),
            MessageHandler(
                filters.Text([BotMessages.BTN_LIST]), logic.show_accounts_list
            ),
        ],
        States.SELECTING_ACTION: [
            CallbackQueryHandler(
                view_handler.ask_master_password, pattern="^action_view"
            ),
            CallbackQueryHandler(edit_handler.ask_new_login, pattern="^action_edit"),
            CallbackQueryHandler(
                logic.ask_delete_confirmation, pattern="^action_delete"
            ),
            CallbackQueryHandler(logic.show_accounts_list, pattern="^back_to_list"),
        ],
        States.CONFIRM_DELETE: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, logic.execute_deletion)
        ],
        States.WAITING_MASTER_VIEW: [
            MessageHandler(
                filters.TEXT & ~filters.COMMAND, view_handler.show_decrypted_credentials
            )
        ],
        States.WAITING_NEW_LOGIN: [
            MessageHandler(
                filters.TEXT & ~filters.COMMAND, edit_handler.ask_new_password
            )
        ],
        States.WAITING_NEW_PASSWORD: [
            CallbackQueryHandler(
                add_logic.handle_password_gen, pattern="^gen_password$"
            ),
            CallbackQueryHandler(add_logic.confirm_gen_pw, pattern="^confirm_gen_pw$"),
            MessageHandler(
                filters.TEXT & ~filters.COMMAND, edit_handler.ask_master_password
            ),
        ],
        States.WAITING_MASTER_EDIT: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, edit_handler.save_changes)
        ],
    },
    fallbacks=[MessageHandler(filters.Text([BotMessages.BTN_CANCEL]), base.cancel)],
    allow_reentry=True,
)
