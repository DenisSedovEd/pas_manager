import logging

from telegram import Message
from telegram.ext import ContextTypes

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


async def delete_message_job(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Коллбэк для JobQueue: удаляет сообщение по ID."""
    chat_id, message_id = context.job.data
    try:
        await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
        logger.info(f"Сообщение {message_id} удалено по таймеру")
    except Exception as e:
        logger.warning(f"Не удалось удалить сообщение {message_id}: {e}")


async def schedule_deletion(
    message: Message, context: ContextTypes.DEFAULT_TYPE, delay: int = 60
):
    """Планирует удаление сообщения через заданное количество секунд."""
    context.job_queue.run_once(
        delete_message_job,
        when=delay,
        data=(message.chat.id, message.message_id),
        name=f"del_{message.message_id}",
    )


async def safe_delete(message: Message | None) -> None:
    """Немедленное удаление сообщения (обычно для сообщений пользователя)."""
    try:
        if message:
            await message.delete()
    except Exception as e:
        logger.warning(f"Не удалось немедленно удалить сообщение: {e}")
