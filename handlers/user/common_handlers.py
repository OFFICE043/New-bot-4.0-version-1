# handlers/user/common_handlers.py
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from keyboards.user_keyboards import get_main_menu_keyboard

async def back_to_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Кез келген диалогты тоқтатып, негізгі менюге оралатын ортақ функция.
    """
    await update.message.reply_text(
        "Asosiy menyuga qaytdingiz.",
        reply_markup=get_main_menu_keyboard()
    )
    # ConversationHandler-ді тоқтату үшін оның соңғы күйін қайтарамыз.
    return ConversationHandler.END
