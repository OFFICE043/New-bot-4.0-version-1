# handlers/admin/panel_navigation.py
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from utils.helpers import is_admin  # (Бұл функцияны utils/helpers.py файлында жасаймыз)
from keyboards.admin_keyboards import get_admin_main_keyboard, get_anime_panel_keyboard, get_settings_panel_keyboard
from keyboards.user_keyboards import get_main_menu_keyboard

async def to_admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context): return
    await update.message.reply_text("Asosiy admin panelidasiz.", reply_markup=get_admin_main_keyboard())

async def to_anime_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context): return
    await update.message.reply_text("🎬 Anime Boshqaruv Paneli", reply_markup=get_anime_panel_keyboard())

async def to_settings_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context): return
    await update.message.reply_text("⚙️ Sozlamalar Boshqaruv Paneli", reply_markup=get_settings_panel_keyboard())

async def switch_to_user_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context): return
    await update.message.reply_text("👤 Siz hozir oddiy foydalanuvchi panelidasiz. Orqaga qaytish uchun /start bosing.", reply_markup=get_main_menu_keyboard())
