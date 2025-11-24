# For all app
start_message = (
    "Приветствую! Это менеджер паролей\n\n"
    "- Добавить новую учетную запись - /add\n"
    "- Просмотреть существующую - /get\n"
    "- Просмотреть список всех - /list"
)

empty_input_error = "❌ <b>Пустой ввод. Повтори попытку.</b>"

master_password_request = "🔐 <b>Введи мастер-пароль:</b>"

service_name_request = "🖥 <b>Введи название сервиса:</b>"

# For get handler


success_decrypt_data_message = (
    "✅ <b>Аккаунт для {service}</b>\n\n"
    "👤 <b>Логин:</b> <code>{username}</code>\n"
    '🔑 <b>Пароль:</b> <span class="tg-spoiler">{password}</span>'
)

account_data_request = (
    "✅ <b>Аккаунт для {service}</b>\n\n⌛️ <b>Время: {at_time}</b>\n\n"
)

# For add handler

start_add_handler = (
    "➕ <b>Начнем добавление нового аккаунта.</b>\n\n🖥 <b>Введи название сервиса:</b>"
)

username_request = "✅ <b>Аккаунт для {service}</b>\n👤 <b>Логин:</b>"

password_request = (
    "✅ <b>Аккаунт для {service}</b>\n\n"
    "👤 <b>Логин:</b> <code>{username}</code>\n"
    "🔑 <b>Пароль:</b>"
)

add_account = (
    "✅ <b>Аккаунт для {service}</b>\n\n👤 <b>Логин:</b> <code>{username}</code>"
)

success_add_account_message = (
    "✅ <b>Аккаунт для {service} успешно добавлен.</b>\n\n"
    "👤 <b>Логин:</b> <code>{username}</code>"
)

# For list handler

start_list_accounts = "<b>📋 Список всех сервисовGHJDT:</b>\n"

item_list_accounts = "<b>{idx}: {account_name}</b>\n"
