# handlers/start.py

import logging
from telegram import Update
from telegram.ext import ContextTypes

from database.db_manager import add_or_update_user, get_user_role
from keyboards.user_keyboards import get_main_menu_keyboard
from keyboards.admin_keyboards import get_admin_main_keyboard
from config import SUPER_ADMINS, VIP_GREETING_STICKER_ID

logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    /start командасын өңдейді. Пайдаланушыны тіркейді және рөліне қарай
    тиісті менюді (User Panel немесе Admin Panel) көрсетеді.
    """
    user = update.effective_user
    
    try:
        # Пайдаланушы деректерін базаға қосу немесе жаңарту
        add_or_update_user(user.id, user.username, user.first_name)
        role = get_user_role(user.id)
        
        # Рөлге байланысты әрекет ету
        if role == 'admin':
            is_super = " (Bosh Admin)" if user.id in SUPER_ADMINS else ""
            await update.message.reply_text(
                f"Salom, Admin{is_super}! Admin paneliga xush kelibsiz.",
                reply_markup=get_admin_main_keyboard()
            )
        elif role == 'vip':
            # VIP пайдаланушыға арнайы стикер жіберу
            if VIP_GREETING_STICKER_ID:
                try:
                    await context.bot.send_sticker(chat_id=user.id, sticker=VIP_GREETING_STICKER_ID)
                except Exception as e:
                    logger.warning(f"VIP stikerini yuborishda xatolik: {e}")
            
            await update.message.reply_text(
                f"Xush kelibsiz, hurmatli VIP a'zo {user.first_name}!",
                reply_markup=get_main_menu_keyboard()
            )
        else: # role == 'user'
            await update.message.reply_text(
                f"Xush kelibsiz, {user.first_name}!",
                reply_markup=get_main_menu_keyboard()
            )
            
    except Exception as e:
        logger.error(f"/start buyrug'ida {user.id} uchun xatolik: {e}")
        await update.message.reply_text("Botda texnik nosozlik yuz berdi. Iltimos, keyinroq qayta urinib ko'ring.")

