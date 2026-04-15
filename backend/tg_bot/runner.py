from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    filters,
)

from backend.core.config import settings
from backend.tg_bot.handlers.accounts import (
    callback_account,
    callback_category,
    cmd_categories,
    cmd_lock,
)
from backend.tg_bot.handlers.unlock import (
    AWAITING_PASSWORD,
    cmd_cancel,
    cmd_unlock,
    receive_password,
)


def run() -> None:
    app = Application.builder().token(settings.tg.telegram_token).build()

    unlock_conv = ConversationHandler(
        entry_points=[CommandHandler("unlock", cmd_unlock)],
        states={
            AWAITING_PASSWORD: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_password)
            ],
        },
        fallbacks=[CommandHandler("cancel", cmd_cancel)],
    )

    app.add_handler(unlock_conv)
    app.add_handler(CommandHandler("categories", cmd_categories))
    app.add_handler(CommandHandler("lock", cmd_lock))
    app.add_handler(CallbackQueryHandler(callback_category, pattern=r"^cat_"))
    app.add_handler(CallbackQueryHandler(callback_account, pattern=r"^acc_"))

    app.run_polling()
