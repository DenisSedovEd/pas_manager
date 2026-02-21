from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CallbackContext,
    CommandHandler,
    MessageHandler,
    filters,
)

from src.old_bot import messages
from src.old_bot.handlers.base_handler import BaseHandler
from src.old_bot.handlers.constants import EditConstraints
from src.repositories import AccountRepository
from src.schemas import EditAccountSchema
from src.services.message_service import schedule_message_deletion


class EditAccountHandler(BaseHandler):

    async def start_editing(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
    ) -> str | int:
        if not await self.check_admin(update):
            return ConversationHandler.END

        context.user_data.clear()

        await update.message.reply_text(
            messages.start_edit_account,
            parse_mode=ParseMode.HTML,
        )
        return EditConstraints.EDIT_SERVICE_NAME

    async def receive_service_name(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
    ) -> str | int:
        service_name = update.message.text.strip()

        if not service_name:
            await update.message.reply_text(
                messages.empty_input_error,
                parse_mode=ParseMode.HTML,
            )
            return EditConstraints.EDIT_SERVICE_NAME

        context.user_data["service_name"] = service_name

        await update.message.reply_text(
            messages.edit_doc,
            parse_mode=ParseMode.HTML,
        )

        await update.message.reply_text(
            messages.username_request.format(service=service_name),
            parse_mode=ParseMode.HTML,
        )
        return EditConstraints.EDIT_USERNAME

    async def recieve_username(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
    ) -> str | int:
        username = update.message.text.strip()
        if not username:
            context.user_data["username"] = None
            return EditConstraints.EDIT_PASSWORD

        context.user_data["username"] = username
        await update.message.reply_text(
            messages.edit_password,
            parse_mode=ParseMode.HTML,
        )
        return EditConstraints.EDIT_PASSWORD

    async def recieve_password(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
    ) -> str | int:
        password = update.message.text
        if not password:
            context.user_data["password"] = None
            return EditConstraints.EDIT_PASSWORD

        context.user_data["password"] = password

        set_msg = await update.message.reply_text(
            messages.master_password_request,
            parse_mode=ParseMode.HTML,
        )

        await schedule_message_deletion(
            message=set_msg,
            context=context,
            delay_seconds=5,
        )

        return EditConstraints.EDIT_MASTER_PASSWORD_CONFIRM

    async def finish_editing(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
    ) -> str | int:
        master_password = update.message.text
        if not master_password:
            await update.message.reply_text(
                messages.empty_input_error,
                parse_mode=ParseMode.HTML,
            )
            return EditConstraints.EDIT_MASTER_PASSWORD_CONFIRM

        try:
            service_name = context.user_data["service_name"]
            username = (
                context.user_data["username"] if context.user_data["username"] else None
            )
            password = (
                context.user_data["password"] if context.user_data["password"] else None
            )

            data = EditAccountSchema(
                service_name=service_name,
                username=username,
                password=password,
            )
            async with AccountRepository as repo:
                await repo.edit_accounts(data=data, master_password=master_password)

            cred_msg = await update.message.reply_text(
                messages.success_decrypt_data_message.format(
                    service=service_name,
                    username=username,
                    password=password,
                ),
                parse_mode=ParseMode.HTML,
            )
            await schedule_message_deletion(
                message=cred_msg,
                context=context,
                delay_seconds=30,
            )

        except Exception as e:
            await update.message.reply_text(f"❌ Произошла ошибка при сохранении: {e}")

        finally:
            context.user_data.clear()

        return ConversationHandler.END


edit_handler_instance = EditAccountHandler()

edit_conv_handler = ConversationHandler(
    entry_points=[
        CommandHandler("edit", edit_handler_instance.start_editing),
    ],
    states={
        EditConstraints.EDIT_SERVICE_NAME: [
            MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                edit_handler_instance.receive_service_name,
            )
        ],
        EditConstraints.EDIT_USERNAME: [
            MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                edit_handler_instance.recieve_username,
            )
        ],
        EditConstraints.EDIT_PASSWORD: [
            MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                edit_handler_instance.recieve_password,
            )
        ],
        EditConstraints.EDIT_MASTER_PASSWORD_CONFIRM: [
            MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                edit_handler_instance.finish_editing,
            )
        ],
    },
    fallbacks=[
        CommandHandler(
            "cancel",
            edit_handler_instance.cancel_command,
        ),
    ],
)
