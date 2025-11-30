from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import (
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

from app.bot import messages
from app.bot.handlers.base_handler import BaseHandler
from app.bot.handlers.constants import AddConstraints
from app.repositories import AccountRepository
from app.schemas import CreateAccountSchema
from app.services.message_service import (
    schedule_message_deletion,
    schedule_messages_deletion,
)


class AddAccountHandler(BaseHandler):

    def __init__(self):
        self.messages_for_del = []

    async def start_add(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
    ) -> str | int:

        if not await self.check_admin(update):
            return ConversationHandler.END

        self.messages_for_del.append(update.message)
        context.user_data.clear()

        self.messages_for_del.append(
            await update.message.reply_text(
                messages.start_add_handler,
                parse_mode=ParseMode.HTML,
            )
        )

        return AddConstraints.ADD_SERVICE_NAME

    async def receive_service_name(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
    ) -> str | int:

        service_name = update.message.text.strip()
        self.messages_for_del.append(update.message)

        if not service_name:
            self.messages_for_del.append(
                await update.message.reply_text(
                    messages.empty_input_error,
                    parse_mode=ParseMode.HTML,
                )
            )
            return AddConstraints.ADD_SERVICE_NAME

        context.user_data["service_name"] = service_name

        self.messages_for_del.append(
            await update.message.reply_text(
                messages.username_request.format(service=service_name),
                parse_mode=ParseMode.HTML,
            )
        )
        return AddConstraints.ADD_USERNAME

    async def receive_username(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
    ) -> str | int:

        username = update.message.text.strip()
        self.messages_for_del.append(update.message)

        if not username:
            self.messages_for_del.append(
                await update.message.reply_text(
                    messages.empty_input_error,
                    parse_mode=ParseMode.HTML,
                )
            )
            return AddConstraints.ADD_USERNAME

        context.user_data["username"] = username
        self.messages_for_del.append(
            await update.message.reply_text(
                messages.password_request.format(
                    service=context.user_data.get("service_name"),
                    username=username,
                ),
                parse_mode=ParseMode.HTML,
            )
        )
        return AddConstraints.ADD_PASSWORD

    async def receive_password(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
    ) -> str | int:
        password = update.message.text
        self.messages_for_del.append(update.message)

        if not password:
            self.messages_for_del.append(
                await update.message.reply_text(
                    messages.empty_input_error,
                    parse_mode=ParseMode.HTML,
                )
            )
            return AddConstraints.ADD_PASSWORD

        context.user_data["password"] = password

        self.messages_for_del.append(
            await update.message.reply_text(
                messages.add_account,
                parse_mode=ParseMode.HTML,
            )
        )
        self.messages_for_del.append(
            await update.message.reply_text(
                messages.master_password_request,
                parse_mode=ParseMode.HTML,
            )
        )

        return AddConstraints.ADD_MASTER_PASSWORD_CONFIRM

    async def finish_add(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
    ) -> str | int:

        master_password = update.message.text
        self.messages_for_del.append(update.message)

        if not master_password:
            self.messages_for_del.append(
                await update.message.reply_text(
                    messages.empty_input_error,
                    parse_mode=ParseMode.HTML,
                )
            )

            return AddConstraints.ADD_MASTER_PASSWORD_CONFIRM

        try:
            data = CreateAccountSchema(
                service_name=context.user_data.get("service_name"),
                username=context.user_data.get("username"),
                password=context.user_data.get("password"),
            )

            async with AccountRepository as repo:
                await repo.create_account(data=data, master_password=master_password)

                self.messages_for_del.append(
                    await update.message.reply_text(
                        f"{messages.add_account.format(service=data.service_name, username=data.username,)}",
                        parse_mode=ParseMode.HTML,
                    )
                )
            await update.message.delete()

        except Exception as e:
            await update.message.delete()

            await update.message.reply_text(f"❌ Произошла ошибка при сохранении: {e}")

        finally:
            await schedule_messages_deletion(
                self.messages_for_del,
                context=context,
                delay_seconds=30,
            )
            context.user_data.clear()

        return ConversationHandler.END


add_handler_instance = AddAccountHandler()

add_conv_handler = ConversationHandler(
    entry_points=[
        CommandHandler("add", add_handler_instance.start_add),
        # MessageHandler(filters.Text(BTN_ADD), add_handler_instance.start_add),
    ],
    states={
        # Состояние 1: Ожидаем название сервиса
        AddConstraints.ADD_SERVICE_NAME: [
            MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                add_handler_instance.receive_service_name,
            )
        ],
        # Состояние 2: Ожидаем логин
        AddConstraints.ADD_USERNAME: [
            MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                add_handler_instance.receive_username,
            )
        ],
        # Состояние 3: Ожидаем пароль
        AddConstraints.ADD_PASSWORD: [
            MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                add_handler_instance.receive_password,
            )
        ],
        # Состояние 4 (Завершающее): Ожидаем мастер-пароль
        AddConstraints.ADD_MASTER_PASSWORD_CONFIRM: [
            MessageHandler(
                filters.TEXT & ~filters.COMMAND, add_handler_instance.finish_add
            )
        ],
    },
    fallbacks=[CommandHandler("cancel", add_handler_instance.cancel_command)],
)
