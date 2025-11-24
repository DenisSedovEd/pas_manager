from telegram import Update
from telegram.ext import ContextTypes

from app.bot.handlers import BaseHandler
from repositories import AccountRepository


class ListAccountsHandler(BaseHandler):

    async def get_list_accounts(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
    ) -> str | int:
        async with AccountRepository as repo:
            result = await repo.list_accounts()
