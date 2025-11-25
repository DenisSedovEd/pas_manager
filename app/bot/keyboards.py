from telegram import ReplyKeyboardMarkup, KeyboardButton

btn_start = ["Начать"]


START_MARKUP = ReplyKeyboardMarkup(
    [[KeyboardButton(btn_start[0])]],
    resize_keyboard=True,
    one_time_keyboard=False,
    input_field_placeholder="Команда для старта",
)
