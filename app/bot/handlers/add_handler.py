from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    filters,
)

from app.bot.handlers import BaseHandler
from app.bot.handlers.constants import AddConstraints
from bot.keyboards import BTN_ADD
from repositories import AccountRepository
from schemas import CreateAccountSchema


class AddAccountHandler(BaseHandler):

    async def start_add(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
    ) -> str | int:
        if not await self.check_admin(update):
            return ConversationHandler.END

        context.user_data.clear()

        await update.message.reply_text(
            "Начнем добавление нового аккаунта. Введи **название сервиса**:",
            parse_mode=ParseMode.MARKDOWN,
        )
        return AddConstraints.ADD_SERVICE_NAME

    async def receive_service_name(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
    ) -> str | int:
        service_name = update.message.text.strip()

        if not service_name:
            await update.message.reply_text("Пустое сообщение, повтори ввод")
            return AddConstraints.ADD_SERVICE_NAME

        context.user_data["service_name"] = service_name

        await update.message.reply_text(
            f"Сервис: {service_name}. Введи **логин**:",
        )
        return AddConstraints.ADD_USERNAME

    async def receive_username(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
    ) -> str | int:
        username = update.message.text.strip()
        if not username:
            await update.message.reply_text(
                "Логин не может быть пустой. Введи еще раз:"
            )
            return AddConstraints.ADD_USERNAME

        context.user_data["username"] = username
        await update.message.reply_text(
            f"Логин {username}. Теперь введи **пароль**:",
            parse_mode=ParseMode.MARKDOWN,
        )
        return AddConstraints.ADD_PASSWORD

    async def receive_password(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
    ) -> str | int:
        password = update.message.text

        if not password:
            await update.message.reply_text(
                "Пароль не может быть пустым. Введи еще раз:"
            )
            return AddConstraints.ADD_PASSWORD

        context.user_data["password"] = password

        await update.message.reply_text(
            f"Добавляю в сервис {context.user_data.get('service_name')} "
            f"пользователя {context.user_data.get('username')}"
            f"🔐 Введи мастер-пароль:",
            parse_mode=ParseMode.MARKDOWN,
        )
        return AddConstraints.ADD_MASTER_PASSWORD_CONFIRM

    async def finish_add(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
    ) -> str | int:
        master_password = update.message.text
        try:
            data = CreateAccountSchema(
                service_name=context.user_data.get("service_name"),
                username=context.user_data.get("username"),
                password=context.user_data.get("password"),
            )

            async with AccountRepository as repo:
                await repo.create_account(data=data, master_password=master_password)

                await update.message.reply_text(
                    f"✅ Аккаунт для **{data.service_name}** успешно добавлен и зашифрован.",
                    parse_mode="Markdown",
                )
            await update.message.delete()

        except Exception as e:
            await update.message.delete()

            await update.message.reply_text(f"❌ Произошла ошибка при сохранении: {e}")

        finally:
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
                filters.TEXT & ~filters.COMMAND, add_handler_instance.receive_username
            )
        ],
        # Состояние 3: Ожидаем пароль
        AddConstraints.ADD_PASSWORD: [
            MessageHandler(
                filters.TEXT & ~filters.COMMAND, add_handler_instance.receive_password
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
