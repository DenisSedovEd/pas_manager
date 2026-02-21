from telegram import ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup

from tg_bot.messages import BotMessages


def get_main_menu():
    keyboard = [
        [BotMessages.BTN_LIST, BotMessages.BTN_VIEW],
        [BotMessages.BTN_ADD, BotMessages.BTN_CANCEL],
    ]
    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
        one_time_keyboard=False,
        is_persistent=True,
    )


def get_generate_pw_keyboard():
    keyboard = [
        [InlineKeyboardButton("🎲 Сгенерировать пароль", callback_data="gen_password")]
    ]
    return InlineKeyboardMarkup(keyboard)
