from datetime import datetime

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import (
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

from app.bot import messages
from app.bot.handlers import BaseHandler
from app.bot.handlers.constants import GetConstraints
from app.repositories import AccountRepository
from app.services.logger import logger
from app.services.message_service import schedule_message_deletion


class GetAccountHandler(BaseHandler):
    async def start_get(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> str | int:
        if not await self.check_admin(update):
            return ConversationHandler.END

        context.user_data.clear()

        await update.message.reply_text(
            messages.service_name_request,
            parse_mode=ParseMode.HTML,
        )
        return GetConstraints.GET_SERVICE_NAME

    async def receive_service_name(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
    ) -> str | int:
        service_name = update.message.text.strip()
        if not service_name:
            await update.message.reply_text(messages.empty_input_error)
            return GetConstraints.GET_SERVICE_NAME

        context.user_data["service_name"] = service_name

        await update.message.reply_text(
            messages.master_password_request,
            parse_mode=ParseMode.HTML,
        )
        return GetConstraints.GET_MASTER_PASSWORD

    async def finish_get(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
    ) -> str | int:
        master_password = update.message.text

        if not master_password:
            await update.message.reply_text(messages.empty_input_error)
            return GetConstraints.GET_MASTER_PASSWORD

        service_name = context.user_data.get("service_name")

        try:
            async with AccountRepository as repo:
                account = await repo.get_account_by_name(
                    service_name=service_name,
                    master_password=master_password,
                )

                await update.message.delete()

                await update.message.reply_text(
                    messages.account_data_request.format(
                        service=service_name,
                        at_time=datetime.now(),
                    ),
                    parse_mode=ParseMode.HTML,
                )

                sent_message = await update.message.reply_text(
                    messages.success_decrypt_data_message.format(
                        service=service_name,
                        username=account.username,
                        password=account.password,
                    ),
                    parse_mode=ParseMode.HTML,
                )

                await schedule_message_deletion(
                    message=sent_message,
                    context=context,
                )

        except Exception as e:
            await update.message.delete()
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
