start_message = (
    f"Приветствую! Это менеджер паролей\n\n"
    f"- Добавить новую учетную запись - /add\n"
    f"- Просмотреть существующую - /get\n"
    f"- Просмотреть список всех - /list"
)

SUCCESS_DECRYPT_DATA_MESSAGE = (
    "✅ <b>Аккаунт для {service}</b>\n\n"
    "👤 <b>Логин:</b> <code>{username}</code>\n"
    '🔑 <b>Пароль:</b> <span class="tg-spoiler">{password}</span>'
)
