import logging

from app.bot.handlers.add_handler import add_conv_handler
from app.bot.handlers.base_handler import BaseHandler
from app.bot.handlers.get_handler import get_conv_handler
from app.bot.handlers.list_handler import list_handler_instance
from telegram.ext import (
    Application,
    CommandHandler,
    JobQueue,
    MessageHandler,
    filters,
)

from app.bot.keyboards import BTN_CANCEL
from app.core.config import settings

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

base_handler_instance = BaseHandler()


def main():
    if not settings.app.telegram_token:
        logger.error("Не найден токен тг")
        return

    job_queue = JobQueue()

    app = (
        Application.builder()
        .token(settings.app.telegram_token)
        .job_queue(job_queue)
        .build()
    )

    app.add_handler(CommandHandler("start", base_handler_instance.start_command))
    app.add_handler(CommandHandler("cancel", base_handler_instance.cancel_command))
    app.add_handler(CommandHandler("list", list_handler_instance.get_list_accounts))

    app.add_handler(add_conv_handler)
    app.add_handler(get_conv_handler)

    app.add_handler(
        MessageHandler(filters.Text(BTN_CANCEL), base_handler_instance.cancel_command)
    )

    logger.info("Бот запущен. Ожидание команд...")
    app.run_polling()


if __name__ == "__main__":
    main()
