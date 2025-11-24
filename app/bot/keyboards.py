from telegram import ReplyKeyboardMarkup


BTN_ADD = "Добавить"
BTN_GET = "Просмотреть"
BTN_LIST = "Список"
BTN_CANCEL = "Отмена"

MAIN_MENU_KEYBOARD = [
    [BTN_ADD, BTN_GET],
    [BTN_LIST, BTN_CANCEL],
]


MAIN_MENU_MARKUP = ReplyKeyboardMarkup(
    MAIN_MENU_KEYBOARD,
    resize_keyboard=True,
    one_time_keyboard=False,
)
