from telegram import Update, ReplyKeyboardRemove
from telegram.constants import ParseMode
from telegram.ext import ContextTypes, ConversationHandler

from app.repositories import RepositoryFactory
from app.bot.handlers import BaseHandler
from app.bot.handlers.constants import AddConstraints
from repositories import AccountRepository
from schemas import CreateAccountSchema


class AddHandler(BaseHandler):
    def __init__(self):
        self.update

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
            parse_mode=ParseMode.MARKDOWN,
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
                await repo.create(data=data, master_password=master_password)

                await update.message.reply_text(
                    f"✅ Аккаунт для **{data.service_name}** успешно добавлен и зашифрован.",
                    parse_mode="Markdown",
                )
        except Exception as e:
            await update.message.reply_text(f"❌ Произошла ошибка при сохранении: {e}")

        finally:
            context.user_data.clear()

        return ConversationHandler.END
