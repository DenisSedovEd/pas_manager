from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters

from app.bot.handlers import BaseHandler, add_handler_instance, get_handler_instance
from app.bot.keyboards import (
    BTN_ADD,
    BTN_CANCEL,
    BTN_GET,
)


class MenuHandler(BaseHandler):
    async def handler_menu_input(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        text = update.message.text
        if text == BTN_ADD:
            return await add_handler_instance.start_add(update, context)

        elif text == BTN_GET:
            return await get_handler_instance.start_get(update, context)

        # elif text == BTN_LIST:
        # return await list_handler_instance.list_command(update, context)

        elif text == BTN_CANCEL:
            return await self.cancel_command(update, context)
        else:
            await update.message.reply_text("Такой команды нет.")


menu_handler_instance = MenuHandler()

menu_message_handler = MessageHandler(
    filters.TEXT & ~filters.COMMAND,
    menu_handler_instance.handler_menu_input,
)
