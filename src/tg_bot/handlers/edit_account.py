from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

from src.dependencies import get_account_service
from src.services.message_service import schedule_deletion, safe_delete
from src.tg_bot.keyboards import get_generate_pw_keyboard, get_main_menu
from src.tg_bot.states import ListAccountStates as States


class EditAccountHandler:
    async def ask_new_login(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        await query.message.delete()

        service_name = context.user_data.get("selected_service")
        context.user_data["mode"] = "edit"  # Устанавливаем режим редактирования

        text = (
            f"✏️ Редактирование **{service_name}**\n\n"
            f"Введите НОВЫЙ логин (или отправьте `-`, чтобы оставить текущий):"
        )
        sent_msg = await update.effective_chat.send_message(
            text, parse_mode="Markdown", reply_markup=get_main_menu()
        )
        await schedule_deletion(sent_msg, context, delay=60)
        return States.WAITING_NEW_LOGIN

    async def ask_new_password(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        await safe_delete(update.message)
        context.user_data["edit_login"] = update.message.text

        text = "Введите НОВЫЙ пароль (или отправьте `-`, чтобы оставить текущий):"
        # Добавляем клавиатуру с кнопкой генерации
        sent_msg = await update.effective_chat.send_message(
            text, reply_markup=get_generate_pw_keyboard()
        )
        await schedule_deletion(sent_msg, context, delay=60)
        return States.WAITING_NEW_PASSWORD

    async def ask_master_password(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        """Этот метод вызывается при ручном вводе пароля текстом"""
        await safe_delete(update.message)
        context.user_data["edit_password"] = update.message.text

        sent_msg = await update.effective_chat.send_message(
            "🔐 Введите мастер-пароль для сохранения изменений:",
            reply_markup=get_main_menu(),
        )
        await schedule_deletion(sent_msg, context, delay=60)
        return States.WAITING_MASTER_EDIT

    async def save_changes(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await safe_delete(update.message)
        master_password = update.message.text

        service_name = context.user_data.get("selected_service")
        new_login = context.user_data.get("edit_login")
        new_password = context.user_data.get("edit_password")

        # Если введено "-", заменяем на None для сервиса
        login_to_save = None if new_login == "-" else new_login
        password_to_save = None if new_password == "-" else new_password

        async with get_account_service() as service:
            try:
                await service.edit_account(
                    service_name=service_name,
                    master_password=master_password,
                    new_username=login_to_save,
                    new_password=password_to_save,
                )
                sent_msg = await update.effective_chat.send_message(
                    "✅ Аккаунт успешно обновлен!", reply_markup=get_main_menu()
                )
                await schedule_deletion(sent_msg, context, delay=10)
            except Exception as e:
                sent_msg = await update.effective_chat.send_message(
                    f"❌ Ошибка сохранения: {str(e)}", reply_markup=get_main_menu()
                )
                await schedule_deletion(sent_msg, context, delay=10)

        # Очистка
        for key in ["edit_login", "edit_password", "mode", "temp_gen_pw"]:
            context.user_data.pop(key, None)

        return ConversationHandler.END


edit_handler = EditAccountHandler()
