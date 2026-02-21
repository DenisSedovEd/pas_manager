import logging

from telegram.ext import (
    Application,
    CommandHandler,
    JobQueue,
    MessageHandler,
    filters,
)

from src.core.config import settings
from tg_bot.handlers.add_account import add_account_conv
from tg_bot.handlers.base import BaseHandler
from tg_bot.handlers.list_accounts import list_accounts_conv
from tg_bot.messages import BotMessages

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

base_handler_instance = BaseHandler()


def main():
    base_handler = BaseHandler()
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
    app.add_handler(CommandHandler("start", base_handler.start))
    app.add_handler(
        MessageHandler(
            filters.Text([BotMessages.BTN_CANCEL]),
            base_handler.cancel,
        )
    )
    app.add_handler(add_account_conv)
    app.add_handler(list_accounts_conv)

    # app.add_handler(CommandHandler("start", base_handler_instance.start_command))
    #
    # app.add_handler(
    #     MessageHandler(
    #         filters.Text(btn_start) & ~filters.COMMAND,
    #         base_handler_instance.start_command,
    #     )
    # )
    #
    # app.add_handler(CommandHandler("cancel", base_handler_instance.cancel_command))
    # app.add_handler(CommandHandler("list", list_handler_instance.get_list_accounts))
    #
    # app.add_handler(add_conv_handler)
    # app.add_handler(get_conv_handler)
    # app.add_handler(edit_conv_handler)

    logger.info("Бот запущен. Ожидание команд...")
    app.run_polling()


if __name__ == "__main__":
    # пускаем на серваке
    main()
