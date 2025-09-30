# handlers/user/anime_search.py
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes, ConversationHandler, MessageHandler, filters, CallbackQueryHandler
)
from telegram.constants import ParseMode
from database import db_manager
from keyboards.user_keyboards import get_anime_search_keyboard, get_back_keyboard, get_main_menu_keyboard

logger = logging.getLogger(__name__)
SEARCH_BY_NAME, SEARCH_BY_CODE, SEARCH_VIA_ADMIN = range(3)

async def to_anime_search_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎬 Anime izlash bo'limi:", reply_markup=get_anime_search_keyboard())

async def back_to_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Asosiy menyuga qaytdingiz.", reply_markup=get_main_menu_keyboard())
    return ConversationHandler.END

# ... search_by_name_start, search_by_name_receive, search_by_code_start, search_by_code_receive функциялары бұрынғыдай...
# (Оларды алдыңғы кодтан көшіріп қойыңыз)

# --- Barcha Animelar (Толық жұмыс істейтін нұсқасы) ---
async def all_animes(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    role = db_manager.get_user_role(update.effective_user.id)
    if role not in ['vip', 'admin']:
        await update.message.reply_text("Bu bo'lim faqat VIP a'zo yoki Adminlar uchun.")
        return

    context.user_data['anime_page'] = 1
    animes = db_manager.get_all_animes_paginated(page=1)
    if not animes:
        await update.message.reply_text("Hozircha animelar mavjud emas.")
        return
        
    text = f"📚 Barcha animelar (1-bet):\n\n"
    for anime in animes:
        text += f"▪️ `{anime['code']}` - {anime['name']}\n"
    
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("Keyingi bet ➡️", callback_data="next_anime_page")]])
    await update.message.reply_text(text, reply_markup=keyboard, parse_mode=ParseMode.MARKDOWN_V2)

async def all_animes_page_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    
    page = context.user_data.get('anime_page', 1) + 1
    context.user_data['anime_page'] = page
    
    animes = db_manager.get_all_animes_paginated(page=page)
    if not animes:
        await query.edit_message_text(text=query.message.text + "\n\nBoshqa animelar topilmadi.")
        return

    text = f"📚 Barcha animelar ({page}-bet):\n\n"
    for anime in animes:
        text += f"▪️ `{anime['code']}` - {anime['name']}\n"
        
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Oldingi bet", callback_data="prev_anime_page"), InlineKeyboardButton("Keyingi bet ➡️", callback_data="next_anime_page")]])
    await query.edit_message_text(text=text, reply_markup=keyboard, parse_mode=ParseMode.MARKDOWN_V2)


# --- Ko'p ko'rilgan 20 anime (Толық жұмыс істейтін нұсқасы) ---
async def top_animes(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    role = db_manager.get_user_role(update.effective_user.id)
    if role not in ['vip', 'admin']:
        await update.message.reply_text("Bu bo'lim faqat VIP a'zo yoki Adminlar uchun.")
        return
        
    top = db_manager.get_top_viewed_animes()
    if not top:
        await update.message.reply_text("Statistika hozircha mavjud emas.")
        return
        
    text = "🏆 Eng ko'p ko'rilgan animelar:\n\n"
    for i, anime in enumerate(top, 1):
        text += f"{i}. {anime['name']} - {anime['views']} marta ko'rilgan\n"
        
    await update.message.reply_text(text)

# --- Admin orqali izlash (ConversationHandler) ---
# ... (Бұл бөлімнің толық кодын да осы жерге қосуға болады)

anime_search_conv_handler = ConversationHandler(...)
