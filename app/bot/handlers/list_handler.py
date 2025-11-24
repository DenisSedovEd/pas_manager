from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from app.bot import messages
from app.bot.handlers import BaseHandler
from app.repositories import AccountRepository


class ListAccountsHandler(BaseHandler):
    async def get_list_accounts(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
    ):
        await update.message.reply_text(
            messages.start_list_accounts,
            parse_mode=ParseMode.HTML,
        )

        async with AccountRepository as repo:
            response = await repo.get_accounts()

        message_parts = []

        for idx, account in enumerate(response, 1):
            message_parts.append(
                messages.item_list_accounts.format(
                    idx=idx,
                    account_name=account,
                )
            )
        final_message = "\n".join(message_parts)
        # message_parts = []
        # template = [
        #     message_parts.append(
        #         messages.item_list_accounts.format(
        #             idx=idx,
        #             account_name=ac.service_name,
        #         )
        #     )
        #     for idx, ac in enumerate(response, 1)
        # ]

        await update.message.reply_text(
            final_message,
            parse_mode=ParseMode.HTML,
        )


list_handler_instance = ListAccountsHandler()
