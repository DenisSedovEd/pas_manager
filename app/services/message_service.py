import logging

from telegram import Message
from telegram.ext import ContextTypes

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


async def delete_secure_message_callback(context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id, message_id = context.job.data

    try:
        await context.bot.delete_message(
            chat_id=chat_id,
            message_id=message_id,
        )
        logger.info("Deleted secure message")
    except Exception as e:
        logger.warning(
            f"Ошибка при удалении сообщения с кредами {message_id}, {chat_id}. Ошибка: {e}"
        )


async def schedule_message_deletion(
    message: Message,
    context: ContextTypes.DEFAULT_TYPE,
    delay_seconds: int = 100,
) -> None:
    chat_id = message.chat.id
    message_id = message.message_id

    job_data = (chat_id, message_id)

    context.job_queue.run_once(
        delete_secure_message_callback,
        delay_seconds,
        data=job_data,
        name=f"del_{message_id}",
    )
    logger.info(f"Запланировано удаление сообщения {message_id}")
