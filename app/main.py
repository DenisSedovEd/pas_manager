import logging

from telegram.ext import (
    Application,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    filters,
)


from app.core.config import settings
from bot.handlers import BaseHandler

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


def main():
    if not settings.app.telegram_token:
        logger.error("Не найден токет тг")
        return

    app = Application.builder().token(settings.app.telegram_token).build()

    base_handler_instance = BaseHandler()

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
