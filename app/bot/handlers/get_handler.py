import logging

from telegram.constants import ParseMode

from app.bot.handlers import BaseHandler
from telegram import Update
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    filters,
)
from app.bot.handlers.constants import GetConstraints

from app.repositories import AccountRepository

from app.bot import messages


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


class GetAccountHandler(BaseHandler):

    async def start_get(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> str | int:
        if not await self.check_admin(update):
            return ConversationHandler.END

        context.user_data.clear()

        await update.message.reply_text(
            "Введи название сервиса:",
            parse_mode=ParseMode.MARKDOWN,
        )
        return GetConstraints.GET_SERVICE_NAME

    async def receive_service_name(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
    ) -> str | int:
        service_name = update.message.text.strip()
        if not service_name:
            await update.message.reply_text("Пустое сообщение. Повтори ввод:")
            return GetConstraints.GET_SERVICE_NAME

        context.user_data["service_name"] = service_name

        await update.message.reply_text(
            f"Сервис {service_name}. 🔐 Введи мастер-пароль:",
            parse_mode=ParseMode.MARKDOWN,
        )
        return GetConstraints.GET_MASTER_PASSWORD

    async def finish_get(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
    ) -> str | int:
        master_password = update.message.text
        service_name = context.user_data.get("service_name")

        try:
            async with AccountRepository as repo:
                account = await repo.get_account_by_name(
                    service_name=service_name,
                    master_password=master_password,
                )

                await update.message.delete()

                sent_message = await update.message.reply_text(
                    messages.SUCCESS_DECRYPT_DATA_MESSAGE.format(
                        service=service_name,
                        username=account.username,
                        password=account.password,
                    ),
                    parse_mode=ParseMode.HTML,
                )

                job_data = (sent_message.chat.id, sent_message.message_id)

                context.job_queue.run_once(
                    self.delete_secure_message,
                    60,
                    data=job_data,
                    name=f"del_{sent_message.message_id}",
                )

        except Exception as e:
            # await update.message.delete()
            logger.error(f"Произошла ошибка в finish_get: {e}")
            await update.message.reply_text(f"❌ Произошла ошибка при дешифровке: {e}")

        finally:
            context.user_data.clear()

        return ConversationHandler.END


get_handler_instance = GetAccountHandler()

get_conv_handler = ConversationHandler(
    entry_points=[CommandHandler("get", get_handler_instance.start_get)],
    states={
        #     Состояние 1
        GetConstraints.GET_SERVICE_NAME: [
            MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                get_handler_instance.receive_service_name,
            )
        ],
        GetConstraints.GET_MASTER_PASSWORD: [
            MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                get_handler_instance.finish_get,
            )
        ],
    },
    fallbacks=[CommandHandler("cancel", get_handler_instance.cancel_command)],
)
