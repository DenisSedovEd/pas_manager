from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from backend.core.config import settings
from backend.core.db import async_session
from backend.core.session import session_manager
from backend.repositories import DatabaseRepository
from backend.repositories.encryption_repository import EncryptionRepository
from backend.services.account_service import AccountService
from backend.services.category_service import CategoryService
from backend.tg_bot.handlers.base import require_session


@require_session
async def cmd_categories(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    async with async_session() as db:
        service = CategoryService(DatabaseRepository(db))
        categories = await service.get_categories()

    if not categories:
        await update.message.reply_text("Категорий пока нет.")
        return

    keyboard = [
        [
            InlineKeyboardButton(
                f"{c.icon} {c.name} ({c.accounts_count})", callback_data=f"cat_{c.id}"
            )
        ]
        for c in categories
    ]
    await update.message.reply_text(
        "📂 Категории:", reply_markup=InlineKeyboardMarkup(keyboard)
    )


@require_session
async def cmd_lock(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    session_manager.close_session(settings.tg.user_id)
    await update.message.reply_text("🔒 Сейф заблокирован.")


async def callback_category(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    if not session_manager.is_active(settings.tg.user_id):
        await query.edit_message_text("🔒 Сессия истекла. Введи /unlock.")
        return

    category_id = query.data.removeprefix("cat_")

    async with async_session() as db:
        account_service = AccountService(DatabaseRepository(db), EncryptionRepository())
        category_service = CategoryService(DatabaseRepository(db))
        accounts = await account_service.get_accounts_by_category(category_id)
        category = await category_service.get_category(category_id)

    if not accounts:
        await query.edit_message_text(
            f"📂 {category.icon} {category.name}\n\nАккаунтов пока нет."
        )
        return

    keyboard = [
        [
            InlineKeyboardButton(
                f"{'🔑' if not a.label else a.label} ({a.login})",
                callback_data=f"acc_{a.id}",
            )
        ]
        for a in accounts
    ]
    await query.edit_message_text(
        f"📂 {category.icon} {category.name}",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def callback_account(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    if not session_manager.is_active(settings.tg.user_id):
        await query.edit_message_text("🔒 Сессия истекла. Введи /unlock.")
        return

    account_id = int(query.data.removeprefix("acc_"))
    master_password = session_manager.get_master_password(settings.tg.user_id)

    async with async_session() as db:
        service = AccountService(DatabaseRepository(db), EncryptionRepository())
        account = await service.get_account_decrypted(account_id, master_password)

    lines = [
        f"🔑 *{account.label or account.login}*",
        f"👤 Логин: `{account.login}`",
        f"🔒 Пароль: `{account.password}`",
    ]
    if account.email:
        lines.append(f"📧 Email: `{account.email}`")
    if account.phone:
        lines.append(f"📱 Телефон: `{account.phone}`")

    await query.edit_message_text("\n".join(lines), parse_mode="Markdown")
