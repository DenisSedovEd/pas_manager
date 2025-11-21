import logging

from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ConversationHandler,
)
from app.bot.handlers import (
    start_command,
    get_password_start,
    receive_service_name,
    receive_master_password,
    cancel_command,
    GET_SERVICE_NAME,
    GET_MASTER_PASSWORD,
    add_password_start,
    receive_add_service_name,
    receive_add_username,
    receive_add_password,
    finalize_add_password,
    ADD_SERVICE_NAME,
    ADD_USERNAME,
    ADD_PASSWORD,
    ADD_MASTER_PASSWORD_CONFIRM,
)
from app.core.config import settings
from app.core.config import settings

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


def main():
    if not settings.app.telegram_token:
        logger.error("Не найден токет тг")
        return

    app = Application.builder().token(settings.app.telegram_token).build()

    get_conv_handler = ConversationHandler(
        entry_points=[CommandHandler("get", get_password_start)],
        states={
            GET_SERVICE_NAME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_service_name)
            ],
            GET_MASTER_PASSWORD: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_master_password)
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel_command)],
        # Начинаем разговор заново, если произошла ошибка
        per_user=True,
    )

    # --- 2. ОБРАБОТЧИК /add (Добавление пароля) ---
    add_conv_handler = ConversationHandler(
        entry_points=[CommandHandler("add", add_password_start)],
        states={
            ADD_SERVICE_NAME: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND, receive_add_service_name
                )
            ],
            ADD_USERNAME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_add_username)
            ],
            ADD_PASSWORD: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_add_password)
            ],
            ADD_MASTER_PASSWORD_CONFIRM: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, finalize_add_password)
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel_command)],
        per_user=True,
    )

    # --- 3. РЕГИСТРАЦИЯ ОБРАБОТЧИКОВ ---
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(get_conv_handler)
    app.add_handler(add_conv_handler)

    logger.info("Бот запущен, ожидает команд")
    app.run_polling()


if __name__ == "__main__":
    main()
