import logging

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

from app.core.config import settings
from app.repositories import with_session, AccountRepository
from schemas import CreateAccountSchema

(
    GET_SERVICE_NAME,
    GET_MASTER_PASSWORD,
    GET_SERVICE_NAME,
    ADD_SERVICE_NAME,
    ADD_PASSWORD,
    ADD_USERNAME,
    ADD_MASTER_PASSWORD_CONFIRM,
) = range(7)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


async def check_admin(update: Update) -> bool:
    logger.info({update.effective_chat.id})
    if update.effective_user.id != settings.app.user_id:
        # logger.info('Зашли в условие, будто не совпадает')
        if update.message:
            await update.message.reply_text(
                "Доступ закрыт. Вы не являетесь владельцем данного бота."
            )

        return False
    return True


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await check_admin(update):
        return
    await update.message.reply_text(
        "Привет. Я менеджер паролей. используй команды /list, /add, /get"
    )


async def get_password_start(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int | bool:
    if not await check_admin(update):
        return False

    if context.args:
        service_name = " ".join(context.args)
        context.user_data["service_name"] = service_name
        await update.message.reply_text(f"Введите **мастер-пароль** для {service_name}")
        return GET_MASTER_PASSWORD
    else:
        await update.message.reply_text("Введите название сервиса")
        return GET_SERVICE_NAME


async def receive_service_name(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    service_name = update.message.text
    context.user_data["service_to_retrieve"] = service_name
    await update.message.reply_text(f"Введите **мастер-пароль** для {service_name}")
    return GET_MASTER_PASSWORD


@with_session
async def receive_master_password(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    service_name = context.user_data.get("service_to_retrieve")
    master_password = update.message.text
    chat_id = update.message.chat_id

    await update.message.reply_text("Дешифрую...")

    try:
        data = await repo.get_decrypted(service_name, master_password)

        if not data:
            await update.message.reply_text(f"Сервис {service_name} не найден.")
            return ConversationHandler.END

        message_text = (
            f"🔐 **Учетные данные для {data.service_name}**\n\n"
            f"Логин: `{data.username}`\n"
            f"Пароль: `{data.password}`\n\n"
            f"⏳ *Сообщение будет удалено через {settings.tg.DELETE_TIMEOUT_SECONDS} секунд.*"
        )
        sent_message = await update.message.reply_text(
            message_text, parse_mode="Markdown"
        )

        context.job_queue.run_once(
            callback=lambda ctx: ctx.bot.delete_message(
                chat_id=chat_id, message_id=sent_message.message_id
            ),
            when=settings.app.delete_timeout_seconds,
            data={"chat_id": chat_id, "message_id": sent_message.message_id},
        )
    except ValueError as e:
        await update.message.reply_text(str(e))
    except NotImplementedError:
        await update.message.reply_text(
            "Ошибка конфигурации: Не реализовано подключение к БД."
        )
    return ConversationHandler.END


@with_session
async def add_password_start(
    update: Update, context: ContextTypes.DEFAULT_TYPE, repo: AccountRepository
) -> int:
    if not await check_admin(update):
        return ConversationHandler.END

    await update.message.reply_text(
        "Введите название сервиса (например, 'Google' или 'GitHub'):"
    )
    # Сохраняем репозиторий для последующих шагов
    context.user_data["repo"] = repo
    return ADD_SERVICE_NAME


async def receive_add_service_name(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    service_name = update.message.text
    context.user_data["service_name"] = service_name
    await update.message.reply_text(
        f"Отлично. Теперь введите логин (username) для сервиса '{service_name}':"
    )
    return ADD_USERNAME


# --- /add: 3. Получение логина ---
async def receive_add_username(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    username = update.message.text
    context.user_data["username"] = username
    await update.message.reply_text(
        "Теперь введите пароль, который нужно зашифровать и сохранить:"
    )
    return ADD_PASSWORD


# --- /add: 4. Получение пароля ---
async def receive_add_password(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    password = update.message.text
    context.user_data["password"] = password
    await update.message.reply_text("Введите **Мастер-пароль** для шифрования данных:")
    return ADD_MASTER_PASSWORD_CONFIRM


# --- /add: 5. Получение Мастер-пароля и сохранение ---
@with_session  # Повторно используем декоратор для получения сессии и repo
async def finalize_add_password(
    update: Update, context: ContextTypes.DEFAULT_TYPE, repo: AccountRepository
) -> int:
    master_password = update.message.text

    # Собираем данные
    try:
        data = CreateAccountSchema(
            service_name=context.user_data["service_name"],
            username=context.user_data["username"],
            password=context.user_data["password"],
        )

        # Шифруем и сохраняем
        await repo.create(data, master_password)

        await update.message.reply_text(
            f"✅ Данные для **{data.service_name}** успешно зашифрованы и сохранены!",
            parse_mode="Markdown",
        )

    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка сохранения данных: {str(e)}")

    # Очищаем временные данные
    for key in ["service_name", "username", "password"]:
        context.user_data.pop(key, None)

    return ConversationHandler.END


async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if not await check_admin(update):
        return
    await update.message.reply_text("Операция отменена")
    return ConversationHandler.END
