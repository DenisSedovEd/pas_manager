from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
    CallbackQueryHandler,
)

from dependencies import get_account_service
from schemas import AccountSchema
from tg_bot.handlers.base import BaseHandler
from tg_bot.keyboards import get_main_menu, get_generate_pw_keyboard
from tg_bot.states import AddAccountStates as States
from tg_bot.states import ListAccountStates

from services.message_service import safe_delete, schedule_deletion
from tg_bot.messages import BotMessages
from utils.password_generator import generate_secure_password, escape_md


class AddAccountHandler:
    async def start_add(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await safe_delete(update.message)
        context.user_data["mode"] = "add"
        sent_msg = await update.effective_chat.send_message(BotMessages.ENTER_SERVICE)
        await schedule_deletion(sent_msg, context, delay=60)
        return States.SERVICE

    async def get_service(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await safe_delete(update.message)
        context.user_data["add_service"] = update.message.text
        sent_msg = await update.effective_chat.send_message(BotMessages.ENTER_LOGIN)
        await schedule_deletion(sent_msg, context, delay=60)
        return States.LOGIN

    async def get_login(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await safe_delete(update.message)
        context.user_data["add_login"] = update.message.text

        sent_msg = await update.effective_chat.send_message(
            BotMessages.ENTER_PASSWORD, reply_markup=get_generate_pw_keyboard()
        )
        await schedule_deletion(sent_msg, context, delay=60)
        return States.PASSWORD

    async def get_password(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await safe_delete(update.message)
        context.user_data["add_password"] = update.message.text

        sent_msg = await update.effective_chat.send_message(BotMessages.ENTER_MASTER)
        await schedule_deletion(sent_msg, context, delay=60)
        return States.MASTER_PASSWORD

    async def handle_password_gen(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        query = update.callback_query
        await query.answer()

        new_pw = generate_secure_password()
        context.user_data["temp_gen_pw"] = new_pw

        escaped_pw = escape_md(new_pw)
        text = f"🎲 Сгенерирован пароль:\n`{escaped_pw}`\n\nИспользовать этот пароль\?"

        keyboard = [
            [
                InlineKeyboardButton(
                    "✅ Да, использовать", callback_data="confirm_gen_pw"
                )
            ],
            [
                InlineKeyboardButton(
                    "🔄 Сгенерировать другой", callback_data="gen_password"
                )
            ],
        ]

        try:
            await query.edit_message_text(
                text=text,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode="MarkdownV2",
            )
        except Exception as e:
            await query.edit_message_text(
                text=f"🎲 Сгенерирован пароль:\n{new_pw}\n\nИспользовать этот пароль?"
            )

        return States.PASSWORD

    async def confirm_gen_pw(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()

        pw = context.user_data.get("temp_gen_pw")
        mode = context.user_data.get("mode", "add")

        await query.message.delete()

        if mode == "add":
            context.user_data["add_password"] = pw
            safe_next_msg = escape_md(BotMessages.ENTER_MASTER)
            sent_msg = await update.effective_chat.send_message(
                f"✅ Пароль принят\\.\n\n{safe_next_msg}",
                parse_mode="MarkdownV2",
                reply_markup=get_main_menu(),
            )
            await schedule_deletion(sent_msg, context, delay=60)
            return States.MASTER_PASSWORD
        else:
            context.user_data["edit_password"] = pw
            sent_msg = await update.effective_chat.send_message(
                "✅ Пароль принят. Введите мастер-пароль:",
                reply_markup=get_main_menu(),
            )
            await schedule_deletion(sent_msg, context, delay=60)
            return ListAccountStates.WAITING_MASTER_EDIT

    async def finish_add(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await safe_delete(update.message)
        master_password = update.message.text

        account_data = AccountSchema(
            service_name=context.user_data["add_service"],
            username=context.user_data["add_login"],
            password=context.user_data["add_password"],
        )

        async with get_account_service() as service:
            try:
                await service.create_account(account_data, master_password)
                sent_msg = await update.effective_chat.send_message(
                    BotMessages.SUCCESS_ADD, reply_markup=get_main_menu()
                )
                await schedule_deletion(sent_msg, context, delay=10)
            except Exception as e:
                await update.effective_chat.send_message(
                    f"❌ Ошибка сохранения: {str(e)}"
                )

        context.user_data.clear()
        return ConversationHandler.END


logic = AddAccountHandler()
base = BaseHandler()

add_account_conv = ConversationHandler(
    entry_points=[MessageHandler(filters.Text([BotMessages.BTN_ADD]), logic.start_add)],
    states={
        States.SERVICE: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, logic.get_service)
        ],
        States.LOGIN: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, logic.get_login)
        ],
        States.PASSWORD: [
            # ВАЖНО: CallbackQueryHandler ДОЛЖНЫ быть первыми
            CallbackQueryHandler(logic.handle_password_gen, pattern="^gen_password$"),
            CallbackQueryHandler(logic.confirm_gen_pw, pattern="^confirm_gen_pw$"),
            MessageHandler(filters.TEXT & ~filters.COMMAND, logic.get_password),
        ],
        States.MASTER_PASSWORD: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, logic.finish_add)
        ],
    },
    fallbacks=[MessageHandler(filters.Text([BotMessages.BTN_CANCEL]), base.cancel)],
    per_message=False,
)
