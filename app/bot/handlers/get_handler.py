import logging
from datetime import datetime

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import (
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

from app.bot import messages
from app.bot.handlers.base_handler import BaseHandler
from app.bot.handlers.constants import GetConstraints
from app.repositories import AccountRepository
from app.services.message_service import (
    schedule_message_deletion,
    schedule_messages_deletion,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


class GetAccountHandler(BaseHandler):
    async def start_get(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> str | int:

        context.user_data["messages_for_del"] = []
        context.user_data["messages_for_del"].append(update.message)
        if not await self.check_admin(update):
            return ConversationHandler.END

        context.user_data.clear()

        context.user_data["messages_for_del"].append(
            await update.message.reply_text(
                messages.service_name_request,
                parse_mode=ParseMode.HTML,
            )
        )
        return GetConstraints.GET_SERVICE_NAME

    async def start_get_from_list(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        query = update.callback_query

        if not await self.check_admin(update):
            return ConversationHandler.END

        await query.answer()

        try:
            service_name = query.data.split(":")[1]
        except IndexError:
            await query.edit_message_text("❌ Ошибка данных аккаунта.")
            return ConversationHandler.END

        context.user_data.clear()

        context.user_data["service_name"] = service_name

        context.user_data["messages_for_del"].append(
            await query.edit_message_text(
                messages.master_password_request,
                parse_mode=ParseMode.HTML,
            )
        )

        return GetConstraints.GET_MASTER_PASSWORD

    async def receive_service_name(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
    ) -> str | int:

        service_name = update.message.text.strip()
        context.user_data["messages_for_del"].append(update.message)
        if not service_name:
            context.user_data["messages_for_del"].append(
                await update.message.reply_text(messages.empty_input_error)
            )
            return GetConstraints.GET_SERVICE_NAME

        context.user_data["service_name"] = service_name

        context.user_data["messages_for_del"].append(
            await update.message.reply_text(
                messages.master_password_request,
                parse_mode=ParseMode.HTML,
            )
        )
        return GetConstraints.GET_MASTER_PASSWORD

    async def finish_get(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
    ) -> str | int:
        master_password = update.message.text
        context.user_data["messages_for_del"].append(update.message)

        if not master_password:
            context.user_data["messages_for_del"].append(
                await update.message.reply_text(messages.empty_input_error)
            )
            return GetConstraints.GET_MASTER_PASSWORD

        service_name = context.user_data.get("service_name")

        try:
            async with AccountRepository as repo:
                account = await repo.get_account_by_name(
                    service_name=service_name,
                    master_password=master_password,
                )

                await update.message.delete()

                context.user_data["messages_for_del"].append(
                    await update.message.reply_text(
                        messages.account_data_request.format(
                            service=service_name,
                            at_time=datetime.now(),
                        ),
                        parse_mode=ParseMode.HTML,
                    )
                )

                context.user_data["messages_for_del"].append(
                    await update.message.reply_text(
                        messages.success_decrypt_data_message.format(
                            service=service_name,
                            username=account.username,
                            password=account.password,
                        ),
                        parse_mode=ParseMode.HTML,
                    )
                )

        except Exception as e:
            await update.message.delete()
            logger.error(f"Произошла ошибка в finish_get: {e}")
            await update.message.reply_text(f"❌ Произошла ошибка при дешифровке: {e}")

        finally:
            await schedule_messages_deletion(
                context.user_data["messages_for_del"],
                context=context,
            )
            context.user_data.clear()

        return ConversationHandler.END


get_handler_instance = GetAccountHandler()

get_conv_handler = ConversationHandler(
    entry_points=[
        CommandHandler("get", get_handler_instance.start_get),
        CallbackQueryHandler(
            get_handler_instance.start_get_from_list,
            pattern=r"^get:.+$",
        ),
    ],
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
